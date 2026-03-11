import pyaudio
import wave
import os
import time
import threading
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QTimer
import audioop
import traceback

class SilenceDetector:
    def __init__(self, threshold=500, silence_timeout=10):
        self.threshold = threshold
        self.silence_timeout = silence_timeout
        self.speaking = False
        self.silence_start = None

    def process_audio(self, audio_data, sample_width):
        rms = audioop.rms(audio_data, sample_width)
        if rms > self.threshold:
            was_speaking = self.speaking
            self.speaking = True
            self.silence_start = None
            return True, was_speaking
        else:
            if self.speaking:
                if self.silence_start is None:
                    self.silence_start = time.time()
                    return False, True
                elif time.time() - self.silence_start >= self.silence_timeout:
                    self.speaking = False
                    self.silence_start = None
                    return False, False
            return False, False

class Recorder(QObject):
    recording_started = Signal()
    recording_stopped = Signal(str)
    listening_started = Signal()
    listening_stopped = Signal()
    status_message = Signal(str)
    start_recording_signal = Signal(bool)
    stop_recording_signal = Signal()  # новый сигнал для остановки записи из потока

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.is_listening = False
        self.auto_mode = False
        self.frames = []
        self.detector = SilenceDetector(settings.silence_threshold, settings.silence_timeout)
        self.after_stop_timer = QTimer()
        self.after_stop_timer.setSingleShot(True)
        self.after_stop_timer.timeout.connect(self.start_listening)

        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.sample_width = pyaudio.get_sample_size(self.format)

        self.listen_thread = None
        self.record_thread = None

        self.start_recording_signal.connect(self._start_recording_from_listen_slot)
        self.stop_recording_signal.connect(self.stop_recording)  # подключаем сигнал

    def update_settings(self):
        self.detector.threshold = self.settings.silence_threshold
        self.detector.silence_timeout = self.settings.silence_timeout

    def start_listening(self):
        print("start_listening: вызван (сработал таймер или ручной запуск)")
        if self.is_listening or self.is_recording:
            print("start_listening: уже активно, пропускаем")
            return
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            self.is_listening = True
            self.listening_started.emit()
            self.status_message.emit("Прослушивание...")
            self.listen_thread = threading.Thread(target=self._listen_loop)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            print("start_listening: поток запущен")
        except Exception as e:
            print(f"Ошибка start_listening: {e}")
            self.status_message.emit(f"Ошибка: {e}")

    def stop_listening(self):
        if not self.is_listening:
            return
        print("stop_listening: начинаем остановку")
        self.is_listening = False
        if self.stream:
            try:
                self.stream.close()
            except Exception as e:
                print(f"Ошибка при закрытии потока прослушивания: {e}")
            self.stream = None
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        self.listening_stopped.emit()
        self.status_message.emit("Прослушивание остановлено")
        print("stop_listening: завершено")

    def _listen_loop(self):
        try:
            while self.is_listening:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                rms = audioop.rms(data, self.sample_width)
                voice_detected, was_speaking = self.detector.process_audio(data, self.sample_width)
                print(f"RMS: {rms}, voice_detected={voice_detected}, was_speaking={was_speaking}, speaking={self.detector.speaking}")
                if voice_detected and not was_speaking:
                    self.start_recording_signal.emit(True)
        except Exception as e:
            print(f"Ошибка в _listen_loop: {e}")
            traceback.print_exc()
        finally:
            print("listen_loop завершён")

    def _start_recording_from_listen_slot(self, auto_mode):
        print("_start_recording_from_listen_slot вызван")
        try:
            if not self.auto_mode:
                print("auto_mode выключен, выход")
                return
            self.stop_listening()
            print("stop_listening выполнен, запускаем запись")
            self.start_recording(auto_mode=auto_mode)
        except Exception as e:
            print(f"Исключение в _start_recording_from_listen_slot: {e}")
            traceback.print_exc()

    def start_recording(self, auto_mode=False):
        if self.is_recording:
            print("start_recording: уже идёт запись")
            return
        print(f"start_recording: начало, auto_mode={auto_mode}")
        self.frames = []
        try:
            print("Открытие потока для записи...")
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            print("Поток для записи открыт")
            self.is_recording = True
            self.recording_started.emit()
            self.status_message.emit("Идёт запись...")
            print("Запуск потока записи...")
            self.record_thread = threading.Thread(target=self._record_loop, args=(auto_mode,))
            self.record_thread.daemon = True
            self.record_thread.start()
            print("Поток записи запущен")
        except Exception as e:
            print(f"ОШИБКА в start_recording: {e}")
            traceback.print_exc()
            self.status_message.emit(f"Ошибка: {e}")

    def _record_loop(self, auto_mode):
        last_voice_time = time.time()
        try:
            while self.is_recording:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
                if auto_mode:
                    rms = audioop.rms(data, self.sample_width)
                    silence_duration = time.time() - last_voice_time
                    print(f"REC: RMS={rms}, silence={silence_duration:.1f}s")
                    if rms > self.detector.threshold:
                        last_voice_time = time.time()
                    elif silence_duration >= self.detector.silence_timeout:
                        print("Тишина превысила таймаут, останавливаем запись")
                        self.stop_recording_signal.emit()  # сигнал для остановки в главном потоке
                        break
        except Exception as e:
            print(f"Ошибка в _record_loop: {e}")
            traceback.print_exc()
        finally:
            if self.stream:
                try:
                    self.stream.close()
                except Exception as e:
                    print(f"Ошибка при закрытии потока записи: {e}")
                self.stream = None
            print("record_loop завершён")

    def stop_recording(self):
        if not self.is_recording:
            return
        print("stop_recording: начало")
        self.is_recording = False
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=1.0)
        if self.stream:
            try:
                self.stream.close()
            except Exception as e:
                print(f"Ошибка при закрытии потока: {e}")
            self.stream = None
        filepath = self._save_recording()
        self.recording_stopped.emit(filepath)
        self.status_message.emit(f"Запись сохранена: {os.path.basename(filepath)}")

        # ========== ТАЙМЕР НА 10 СЕКУНД ПЕРЕД СЛЕДУЮЩИМ ЦИКЛОМ ==========
        # Здесь будет пауза перед повторным прослушиванием (заменится на действия ИИ)
        if self.auto_mode:
            print("Запуск таймера на 10 секунд (пауза перед следующим прослушиванием)")
            self.after_stop_timer.start(10000)
        # =================================================================
        print("stop_recording: завершено")

    def _save_recording(self):
        if not self.frames:
            print("Нет фреймов для сохранения")
            return ""
        os.makedirs(self.settings.output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"recording_{timestamp}.wav"
        filepath = os.path.join(self.settings.output_dir, filename)
        try:
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.sample_width)
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))
            print(f"Файл сохранён: {filepath}")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            traceback.print_exc()
            self.status_message.emit(f"Ошибка сохранения: {e}")
            return ""
        return filepath

    def toggle_auto_mode(self):
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            self.start_listening()
        else:
            self.stop_listening()
            if self.is_recording:
                self.stop_recording()
        return self.auto_mode

    def cleanup(self):
        self.stop_listening()
        if self.is_recording:
            self.stop_recording()
        if self.audio:
            self.audio.terminate()