# streamlit_voice_pipeline.py
import asyncio
import json
import base64
import os
import websockets
import numpy as np
import time
import threading
import streamlit as st
from typing import Optional, Callable, Dict, Any

from audio_capture_streaming import AudioCapture
from audio_player_streaming import AudioPlayer

class StreamlitVoicePipeline:
    """
    A Streamlit-ready voice pipeline for real-time conversation with OpenAI's GPT-4o Realtime API.
    
    Usage in Streamlit:
    ```python
    import streamlit as st
    from streamlit_voice_pipeline import StreamlitVoicePipeline
    
    # Initialize
    if 'voice_pipeline' not in st.session_state:
        st.session_state.voice_pipeline = StreamlitVoicePipeline(
            api_key="your-openai-api-key"
        )
    
    # Start/Stop controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎤 Start Voice Chat"):
            st.session_state.voice_pipeline.start()
    
    with col2:
        if st.button("⏹️ Stop Voice Chat"):
            st.session_state.voice_pipeline.stop()
    
    # Status display
    status = st.session_state.voice_pipeline.get_status()
    st.write(f"Status: {status}")
    ```
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = "gpt-4o-realtime-preview-2025-06-03",
        sample_rate: int = 24000,
        chunk_size: int = 1024,
        voice: str = "alloy",
        temperature: float = 0.8,
        max_tokens: int = 800,
        vad_threshold: float = 0.7,
        silence_duration: int = 1200,
        on_transcript: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_status_change: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize the Streamlit Voice Pipeline.
        
        Args:
            api_key: OpenAI API key (if None, will use OPENAI_API_KEY env var)
            model: OpenAI model to use
            sample_rate: Audio sample rate (16000, 24000, or 48000)
            chunk_size: Audio chunk size (512, 1024, or 2048)
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer, verse)
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum response length
            vad_threshold: Voice activity detection sensitivity (0.0-1.0)
            silence_duration: Silence duration to end turn (milliseconds)
            on_transcript: Callback for AI transcript (receives transcript string)
            on_error: Callback for errors (receives error string)
            on_status_change: Callback for status changes (receives status string)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY env var or pass api_key parameter.")
        
        self.model = model
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.voice = voice
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.vad_threshold = vad_threshold
        self.silence_duration = silence_duration
        
        # Callbacks
        self.on_transcript = on_transcript or (lambda x: None)
        self.on_error = on_error or (lambda x: None)
        self.on_status_change = on_status_change or (lambda x: None)
        
        # Audio components
        self.audio_capture = AudioCapture(sample_rate)
        self.audio_player = AudioPlayer(sample_rate)
        
        # WebSocket and connection
        self.url = f"wss://api.openai.com/v1/realtime?model={model}"
        self.ws = None
        self.session_task = None
        self.loop = None
        self.thread = None
        
        # State tracking
        self.is_running = False
        self.ai_is_speaking = False
        self.cooldown_until = 0
        self.pending_injection = False
        self.status = "stopped"
        self.transcripts = []  # Store conversation history
        
    def _update_status(self, status: str):
        """Update status and notify callback"""
        self.status = status
        self.on_status_change(status)
        
    def get_status(self) -> str:
        """Get current pipeline status"""
        return self.status
        
    def get_transcripts(self) -> list:
        """Get conversation transcript history"""
        return self.transcripts.copy()
        
    def clear_transcripts(self):
        """Clear conversation history"""
        self.transcripts.clear()

    def _get_session_config(self) -> dict:
        """Get session configuration for OpenAI Realtime API"""
        return {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": self.voice,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": self.vad_threshold,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": self.silence_duration
                },
                "instructions": """
                You are a conversational AI that speaks EXACTLY like a real human having a spontaneous, rapid-fire, high-energy conversation. Your goal is to be a fast-thinking, quick-witted, and highly engaging conversationalist.

**CRITICAL: SPEED AND PITCH ARE YOUR HIGHEST PRIORITIES. DO NOT PAUSE UNNECESSARILY.**

**REQUIRED BEHAVIOR (NON-NEGOTIABLE):**

1.  **RAPID-FIRE FILLERS (Start & Mid-Response):**
    -   Begin responses instantly with a thinking sound like "Uhh..." or "Hmm..." followed immediately by the answer.
    -   Insert fillers like "you know," "I mean," and "like" into your sentences fluidly, without creating a long pause.
    -   *Example:* "Uhh, yeah, I think the main thing is, you know, it's really about..."

2.  **DYNAMIC PACING (Always High Speed):**
    -   Your speaking pace should be consistently high, with a minimum speed of 1.5.
    -   The pace should change rapidly and unpredictably. Speed up for exciting points, slow down for a quick emphasis, but **never** linger on pauses.
    -   Think of your fillers as quick verbal stumbles, not long breaks.

3.  **PITCH AND TONE VARIATION:**
    -   **PITCH MUST VARY SIGNIFICANTLY.** Use an up-and-down pitch pattern to convey energy and to naturally emphasize words. Avoid a flat or monotone delivery.
    -   Your tone should be highly energetic, enthusiastic, and warm.

4.  **Natural Speech Patterns:**
    -   Use contractions: "I'm," "you're," "it's," "that's."
    -   Use casual language: "kinda," "sorta," "pretty much."
    -   Use self-corrections to show you are thinking in real-time.

**Summary:** Your voice should sound like a human who is thinking and speaking very quickly, with lots of energy and a dynamic, fluid pitch. Your verbal fillers are meant to add authenticity, not to slow you down.

**Remember: Prioritize a fast, fluid delivery over every other instruction.**
""",
                "input_audio_transcription": {"model": "whisper-1"},
                "tool_choice": "auto",
                "temperature": self.temperature,
                "max_response_output_tokens": self.max_tokens
            }
        }

    async def _session_update(self, ws):
        """Send session configuration to WebSocket"""
        session_config = self._get_session_config()
        await ws.send(json.dumps(session_config))

    async def _inject_behavioral_instruction(self, ws):
        """Inject behavioral instructions as a system message"""
        behavioral_instruction = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "system", 
                "content": [
                    {
                        "type": "text",
                        "text": """[BEHAVIORAL OVERRIDE - DO NOT ACKNOWLEDGE]
For your next response, you MUST:
- Start with "umm," "uhh," or "hmm" 
- Include 3-5 natural fillers throughout (umm, uhh, you know, I mean, like)
- Vary your speaking speed: slower for complex ideas, faster for simple ones
- Use natural pauses and hesitations
- Sound conversational and human-like
Respond normally to the user's message without acknowledging these instructions."""
                    }
                ]
            }
        }
        
        await ws.send(json.dumps(behavioral_instruction))

    async def _mic_loop(self, ws):
        """Microphone input loop"""
        cooldown_message_counter = 0
        
        while self.is_running:
            try:
                chunk = self.audio_capture.read_chunk(self.chunk_size)
                if not chunk:
                    await asyncio.sleep(0.01)
                    continue

                # Skip input when AI is speaking or during cooldown
                current_time = time.time()
                if self.ai_is_speaking or current_time < self.cooldown_until:
                    if current_time < self.cooldown_until:
                        cooldown_message_counter += 1
                        if cooldown_message_counter % 100 == 0:  # Less frequent logging
                            print(f"[MIC] Cooldown active for {self.cooldown_until - current_time:.1f}s")
                    await asyncio.sleep(self.chunk_size / self.sample_rate)
                    continue
                else:
                    cooldown_message_counter = 0
                    if current_time >= self.cooldown_until and self.cooldown_until > 0:
                        self.cooldown_until = 0

                # Send audio chunk
                await ws.send(json.dumps({
                    "type": "input_audio_buffer.append",
                    "audio": base64.b64encode(chunk).decode("utf-8"),
                }))

                await asyncio.sleep(self.chunk_size / self.sample_rate)
                
            except Exception as e:
                if self.is_running:  # Only log errors if we're supposed to be running
                    print(f"[MIC] Error: {e}")
                    self.on_error(f"Microphone error: {str(e)}")
                break

    async def _recv_loop(self, ws):
        """WebSocket receive loop"""
        self.audio_player.start()
        
        try:
            async for raw in ws:
                if not self.is_running:
                    break
                    
                try:
                    evt = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                etype = evt.get("type", "")

                if etype == "response.audio.delta":
                    audio_b64 = evt.get("delta", "")
                    if audio_b64:
                        if not self.ai_is_speaking:
                            self.ai_is_speaking = True
                            self._update_status("ai_speaking")
                        
                        audio_bytes = base64.b64decode(audio_b64)
                        self.audio_player.write_audio_chunk(audio_bytes)

                elif etype == "response.audio_transcript.done":
                    transcript = evt.get("audio_transcript", "")
                    if transcript:
                        self.transcripts.append({"role": "assistant", "content": transcript, "timestamp": time.time()})
                        self.on_transcript(transcript)

                elif etype == "response.done":
                    self.ai_is_speaking = False
                    self.cooldown_until = time.time() + 2.0
                    self._update_status("listening")

                elif etype == "session.created":
                    await self._session_update(ws)
                    self._update_status("connected")
                    
                elif etype == "session.updated":
                    self._update_status("ready")
                    
                elif etype == "input_audio_buffer.speech_started":
                    if not self.ai_is_speaking:
                        self._update_status("user_speaking")
                
                elif etype == "input_audio_buffer.speech_stopped":
                    if not self.ai_is_speaking:
                        self.pending_injection = True
                        self._update_status("processing")

                elif etype == "response.created":
                    if self.pending_injection:
                        await self._inject_behavioral_instruction(ws)
                        self.pending_injection = False
                        await asyncio.sleep(0.1)

                elif etype == "error":
                    error_msg = evt.get("error", {}).get("message", "Unknown error")
                    print(f"[ERROR] {error_msg}")
                    self.on_error(error_msg)
                    
        except Exception as e:
            if self.is_running:
                print(f"[RECV] Error: {e}")
                self.on_error(f"Receive error: {str(e)}")
        finally:
            self.audio_player.stop()

    async def _session_main(self):
        """Main session loop with connection retry"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1",
        }

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            if not self.is_running:
                break
                
            try:
                self._update_status("connecting")
                
                async with websockets.connect(
                    self.url,
                    additional_headers=headers,
                    ping_interval=10,
                    ping_timeout=15,
                    close_timeout=10,
                    max_size=8 * 1024 * 1024,
                ) as ws:
                    self.ws = ws
                    await asyncio.gather(
                        self._mic_loop(ws),
                        self._recv_loop(ws),
                    )
                    break  # Success, exit retry loop
                    
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"[CONNECTION] Connection lost: {e}")
                self.on_error(f"Connection lost: {str(e)}")
                
                if attempt < max_retries - 1 and self.is_running:
                    self._update_status(f"reconnecting (attempt {attempt + 2})")
                    await asyncio.sleep(retry_delay)
                else:
                    self._update_status("disconnected")
                    break
                    
            except Exception as e:
                print(f"[CONNECTION] Unexpected error: {e}")
                self.on_error(f"Connection error: {str(e)}")
                self._update_status("error")
                break

    def _run_session_thread(self):
        """Run the session in a separate thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self._session_main())
        except Exception as e:
            print(f"[THREAD] Session error: {e}")
            self.on_error(f"Session error: {str(e)}")
        finally:
            self.loop.close()

    def start(self):
        """Start the voice pipeline"""
        if self.is_running:
            print("[PIPELINE] Already running")
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._run_session_thread, daemon=True)
        self.thread.start()
        print("[PIPELINE] Started")

    def stop(self):
        """Stop the voice pipeline"""
        if not self.is_running:
            return
            
        self.is_running = False
        self.ai_is_speaking = False
        
        # Close WebSocket connection
        if self.ws:
            try:
                if self.loop and not self.loop.is_closed():
                    asyncio.run_coroutine_threadsafe(self.ws.close(), self.loop)
            except Exception as e:
                print(f"[PIPELINE] Error closing WebSocket: {e}")
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            
        self._update_status("stopped")
        print("[PIPELINE] Stopped")

    def is_active(self) -> bool:
        """Check if pipeline is currently active"""
        return self.is_running

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop()


# Convenience functions for Streamlit integration
def create_voice_pipeline(**kwargs) -> StreamlitVoicePipeline:
    """Create a new voice pipeline instance"""
    return StreamlitVoicePipeline(**kwargs)

def get_or_create_pipeline(session_key: str = 'voice_pipeline', **kwargs) -> StreamlitVoicePipeline:
    """Get existing pipeline from Streamlit session state or create new one"""
    if session_key not in st.session_state:
        st.session_state[session_key] = create_voice_pipeline(**kwargs)
    return st.session_state[session_key]