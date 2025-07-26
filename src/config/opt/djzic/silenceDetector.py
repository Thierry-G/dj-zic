import numpy as np
import loggerConfig

class SilenceDetector:
    def __init__(self, enable_logging=True):
        self.CHUNK = 512
        self.SILENCE_THRESHOLD_RMS = 3.15
        self.SILENCE_THRESHOLD_MAX = 15
        self.SILENCE_DURATION = 3  # seconds
        self.FRAME_RATE = 48000
        self.RMS_MIN = 1.5
        self.logger = loggerConfig.setup_logging(enable_logging=enable_logging)
        self.enable_logging = enable_logging

        # Precalculate silence threshold in chunks
        self.silence_chunk_threshold = int(self.FRAME_RATE / self.CHUNK * self.SILENCE_DURATION)
        self.silent_chunks = 0

    def is_silent(self, data: np.ndarray):
        # Compute RMS and max amplitude using vectorized NumPy operations
        rms = np.sqrt(np.mean(data ** 2))
        max_amplitude = np.max(np.abs(data))

        # Update silent chunk count based on thresholds
        if rms < self.SILENCE_THRESHOLD_RMS and max_amplitude < self.SILENCE_THRESHOLD_MAX:
            self.silent_chunks += 1
        else:
            self.silent_chunks = 0

        # Check if silence duration or minimum RMS is met
        if self.silent_chunks > 5 or self.silent_chunks > self.silence_chunk_threshold or rms < self.RMS_MIN:
            if self.enable_logging and (self.silent_chunks > 5 or ...):
                self.logger.info("Silence detected")
            return True
        
        # Debugging output
        #print(f"RMS: {rms:.2f}, Max Amplitude: {max_amplitude:.2f}, Silent Chunks: {self.silent_chunks}")
        return False
