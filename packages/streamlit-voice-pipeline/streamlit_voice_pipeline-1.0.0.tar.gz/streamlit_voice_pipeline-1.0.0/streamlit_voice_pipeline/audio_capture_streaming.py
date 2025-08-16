import sounddevice as sd
import numpy as np
from typing import Optional


class AudioCapture:
    """Handles microphone audio capture with verbose debug logging."""

    def __init__(self, sample_rate: int = 24000, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.stream: Optional[sd.InputStream] = None
        self.device_info = None
        print(f"[AUDIO_INPUT][INIT] 🎙️ Sample Rate: {sample_rate} Hz, Chunk Size: {chunk_size}")

    def start(self):
        """Initialize microphone stream."""
        print("[AUDIO_INPUT] 🔍 Listing audio devices...")
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            print(f"  [{i}] {dev['name']} (input channels: {dev['max_input_channels']})")

        try:
            print("[AUDIO_INPUT] 🎙️ Opening microphone stream...")
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.int16,
                blocksize=self.chunk_size,
                callback=None  # we use blocking read
            )
            self.stream.start()
            self.device_info = self.stream.device
            print(f"[AUDIO_INPUT] ✅ Microphone stream started on device: {self.device_info}")
        except Exception as e:
            print(f"[ERROR][AUDIO_INPUT] ❌ Failed to start microphone: {e}")
            self.stream = None

    def read_chunk(self, chunk_size: Optional[int] = None) -> Optional[bytes]:
        """Read a chunk of audio data from the microphone."""
        if not self.stream or not self.stream.active:
            print("[DEBUG][AUDIO_INPUT] ⚠ No active mic stream — starting it now...")
            self.start()
            if not self.stream:
                return None

        try:
            chunk_size = chunk_size or self.chunk_size
            audio_data, _ = self.stream.read(chunk_size)
            print(f"[AUDIO_INPUT] 📥 Captured {len(audio_data)} frames from mic")
            return audio_data.tobytes()
        except Exception as e:
            print(f"[ERROR][AUDIO_INPUT] ❌ Error reading from mic: {e}")
            return None

    def stop(self):
        """Stop the microphone stream."""
        if self.stream:
            print("[AUDIO_INPUT] 🛑 Stopping microphone stream...")
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("[AUDIO_INPUT] ✅ Microphone stopped")
