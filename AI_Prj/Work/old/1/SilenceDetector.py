import math
import audioop
import time

class SilenceDetector:
    def __init__(self, threshold=500, silence_timeout=10):
        self.threshold = threshold      # порог громкости (зависит от формата)
        self.silence_timeout = silence_timeout  # секунд тишины для останова
        self.speaking = False
        self.silence_start = None

    def process_audio(self, audio_data, sample_width):
        """Анализирует блок аудио, возвращает True, если detected voice, и обновляет состояние"""
        rms = audioop.rms(audio_data, sample_width)
        if rms > self.threshold:
            self.speaking = True
            self.silence_start = None
            return True
        else:
            if self.speaking:
                if self.silence_start is None:
                    self.silence_start = time.time()
                elif time.time() - self.silence_start >= self.silence_timeout:
                    self.speaking = False
                    self.silence_start = None
                    return False   # сигнал, что пора остановить запись
            return False