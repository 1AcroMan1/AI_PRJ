import sys
import os
import threading
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import QTimer, Qt
import pyaudio
import wave

class VoiceRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.audio_frames = []
        self.audio = None
        self.stream = None
        
        # Настройки аудио
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        
        self.init_ui()
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Простой диктофон")
        self.setFixedSize(300, 200)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Метка статуса
        self.status_label = QLabel("Готов к записи")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # Кнопка записи
        self.record_button = QPushButton("Начать запись")
        self.record_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border: 2px solid #2196F3;
                border-radius: 10px;
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)
        
        # Таймер для обновления времени записи
        self.record_timer = QTimer()
        self.record_timer.timeout.connect(self.update_record_time)
        self.record_start_time = None
        self.record_duration = 0
        
        # Метка времени записи
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #666;")
        layout.addWidget(self.time_label)
        
    def toggle_recording(self):
        """Переключение режима записи"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Начать запись"""
        try:
            # Инициализация PyAudio
            self.audio = pyaudio.PyAudio()
            self.audio_frames = []
            
            # Открытие потока для записи
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            self.is_recording = True
            self.record_start_time = datetime.now()
            self.record_duration = 0
            
            # Обновление интерфейса
            self.record_button.setText("Остановить запись")
            self.record_button.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    font-weight: bold;
                    padding: 15px;
                    border: 2px solid #F44336;
                    border-radius: 10px;
                    background-color: #F44336;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
                QPushButton:pressed {
                    background-color: #B71C1C;
                }
            """)
            self.status_label.setText("Идет запись...")
            self.status_label.setStyleSheet("font-size: 14px; color: #F44336; font-weight: bold; margin: 10px;")
            
            # Запуск таймера для обновления времени
            self.record_timer.start(1000)  # Обновление каждую секунду
            
            # Запуск потока для записи аудио
            self.record_thread = threading.Thread(target=self.record_audio)
            self.record_thread.daemon = True
            self.record_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать запись:\n{str(e)}")
            self.cleanup_audio()
    
    def record_audio(self):
        """Запись аудио в отдельном потоке"""
        try:
            while self.is_recording and self.stream:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.audio_frames.append(data)
        except Exception as e:
            print(f"Ошибка записи: {e}")
    
    def stop_recording(self):
        """Остановить запись"""
        self.is_recording = False
        self.record_timer.stop()
        
        # Обновление интерфейса
        self.record_button.setText("Начать запись")
        self.record_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border: 2px solid #2196F3;
                border-radius: 10px;
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.status_label.setText("Запись сохранена")
        self.status_label.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold; margin: 10px;")
        
        # Сохранение записи
        self.save_recording()
        
        # Очистка аудио ресурсов
        self.cleanup_audio()
    
    def update_record_time(self):
        """Обновление времени записи"""
        if self.record_start_time:
            self.record_duration += 1
            minutes = self.record_duration // 60
            seconds = self.record_duration % 60
            self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def save_recording(self):
        """Сохранить записанное аудио в файл"""
        if not self.audio_frames:
            QMessageBox.warning(self, "Предупреждение", "Нет записанных данных")
            return
        
        try:
            # Создание папки для записей, если её нет
            recordings_dir = "recordings"
            if not os.path.exists(recordings_dir):
                os.makedirs(recordings_dir)
            
            # Генерация имени файла с временной меткой
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(recordings_dir, f"recording_{timestamp}.wav")
            
            # Сохранение в WAV файл
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.audio_frames))
            
            # Показать сообщение об успешном сохранении
            QMessageBox.information(self, "Успех", f"Запись сохранена в:\n{filename}")
            
            # Сброс времени
            self.time_label.setText("00:00")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить запись:\n{str(e)}")
    
    def cleanup_audio(self):
        """Очистка аудио ресурсов"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            if self.audio:
                self.audio.terminate()
                self.audio = None
                
        except Exception as e:
            print(f"Ошибка при очистке: {e}")
    
    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.is_recording:
            self.stop_recording()
        self.cleanup_audio()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyle('Fusion')
    
    recorder = VoiceRecorder()
    recorder.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()