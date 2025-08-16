import sounddevice as sd
import numpy as np
from typing import Optional, Any

class AudioPlayer:
    """Handles continuous audio playback for real-time streaming."""
    
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate
        self.stream: Optional[sd.OutputStream] = None
        self.audio_chunks_received = 0
        self.total_audio_bytes = 0

    def start(self):
        """Start the audio player stream."""
        if self.stream and self.stream.active:
            print("[AUDIO_OUTPUT] ⚠ Player already running")
            return

        print(f"[AUDIO_OUTPUT] 🎧 Starting audio playback stream ({self.sample_rate}Hz)")
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16
        )
        self.stream.start()

    def write_audio_chunk(self, audio_data: bytes) -> bool:
        """
        Play a single audio chunk (PCM16 bytes).
        :param audio_data: raw PCM16 mono bytes
        """
        if not self.stream or not self.stream.active:
            print("[AUDIO_OUTPUT] ⚠ Player not active")
            return False

        try:
            # Convert bytes → numpy array for sounddevice
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            self.audio_chunks_received += 1
            self.total_audio_bytes += len(audio_data)
            print(f"[AUDIO_OUTPUT] ▶ Playing chunk #{self.audio_chunks_received} ({len(audio_data)} bytes)")

            self.stream.write(audio_array)
            return True
        except Exception as e:
            print(f"[AUDIO_OUTPUT] ⚠ Error writing to audio player: {e}")
            return False

    def stop(self):
        """Stop and clean up the audio player."""
        print(f"\n[AUDIO_OUTPUT] 🛑 Playback completed")
        print(f"[AUDIO_OUTPUT] Total chunks played: {self.audio_chunks_received}")
        print(f"[AUDIO_OUTPUT] Total bytes played: {self.total_audio_bytes}")

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.audio_chunks_received = 0
        self.total_audio_bytes = 0
        print("[AUDIO_OUTPUT] ✓ Audio player stopped")
