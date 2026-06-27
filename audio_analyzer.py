import numpy as np
import sounddevice as sd
import librosa

class AudioAnalyzer:
    def __init__(self, sample_rate=22050, chunk_duration=0.5):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_samples = int(self.sample_rate * self.chunk_duration)
        self.volume_threshold = 0.15 # Needs tuning based on mic sensitivity
        self.stream = None
        self.current_audio_chunk = np.zeros(self.chunk_samples)
        
    def audio_callback(self, indata, frames, time, status):
        """ This is called by sounddevice for each audio block """
        if status:
            print(status)
        # Flatten and save the audio chunk
        self.current_audio_chunk = indata[:, 0].copy()

    def start_listening(self):
        """ Start the non-blocking audio stream """
        self.stream = sd.InputStream(
            samplerate=self.sample_rate, 
            channels=1, 
            callback=self.audio_callback,
            blocksize=self.chunk_samples
        )
        self.stream.start()

    def stop_listening(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def detect_yelling(self):
        """ Calculate RMS energy to detect loud noises (yelling/screaming) """
        if self.current_audio_chunk is not None and len(self.current_audio_chunk) > 0:
            # Calculate RMS energy of the chunk
            rms = librosa.feature.rms(y=self.current_audio_chunk)[0]
            mean_rms = np.mean(rms)
            
            is_yelling = mean_rms > self.volume_threshold
            return is_yelling, mean_rms
        return False, 0.0
