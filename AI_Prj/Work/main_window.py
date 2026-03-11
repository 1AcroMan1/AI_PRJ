from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                               QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt, Slot
from recorder import Recorder
from settings import Settings
from hotkey_manager import HotkeyManager
from settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.recorder = Recorder(self.settings)
        self.hotkey_manager = HotkeyManager()

        self.setWindowTitle("Диктофон с авторежимом")
        self.setFixedSize(400, 300)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.status_label = QLabel("Готов")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(self.status_label)

        self.mode_label = QLabel("Режим: ручной")
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setStyleSheet("font-size: 12px; color: gray;")
        layout.addWidget(self.mode_label)

        self.record_button = QPushButton("Начать запись")
        self.record_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.record_button.clicked.connect(self.on_record_clicked)
        layout.addWidget(self.record_button)

        self.auto_button = QPushButton("Включить авторежим")
        self.auto_button.clicked.connect(self.on_toggle_auto)
        layout.addWidget(self.auto_button)

        self.settings_button = QPushButton("Настройки")
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # Подключаем сигналы рекордера
        self.recorder.recording_started.connect(self.on_recording_started)
        self.recorder.recording_stopped.connect(self.on_recording_stopped)
        self.recorder.listening_started.connect(self.on_listening_started)
        self.recorder.listening_stopped.connect(self.on_listening_stopped)
        self.recorder.status_message.connect(self.on_status_message)

        # Подключаем сигналы хоткеев
        self.hotkey_manager.toggle_record.connect(self.on_toggle_record_hotkey)
        self.hotkey_manager.toggle_auto.connect(self.on_toggle_auto_hotkey)
        self.hotkey_manager.open_settings.connect(self.open_settings)

        # Регистрируем хоткеи
        self.hotkey_manager.register_all(self.settings)

        #Сигнал на диалог настроек для закрытия
        self.settings_dialog = None

        self.update_ui()

    def on_record_clicked(self):
        if self.recorder.auto_mode:
            QMessageBox.information(self, "Информация",
                                    "В авторежиме запись управляется автоматически. Отключите авторежим для ручного управления.")
            return
        if not self.recorder.is_recording:
            self.recorder.start_recording()
        else:
            self.recorder.stop_recording()

    def on_toggle_auto(self):
        new_mode = self.recorder.toggle_auto_mode()
        self.auto_button.setText("Отключить авторежим" if new_mode else "Включить авторежим")
        self.update_ui()

    @Slot()
    def on_toggle_record_hotkey(self):
        # В авторежиме хоткей отключает авторежим (согласно заданию: отключение автоматического прослушивания производится на хоткей)
        if self.recorder.auto_mode:
            self.recorder.toggle_auto_mode()
            self.auto_button.setText("Включить авторежим")
        else:
            if not self.recorder.is_recording:
                self.recorder.start_recording()
            else:
                self.recorder.stop_recording()
        self.update_ui()

    @Slot()
    def on_toggle_auto_hotkey(self):
        self.on_toggle_auto()

    @Slot()
    def open_settings(self):
        if self.settings_dialog is not None and self.settings_dialog.isVisible():
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            return

        # Создаём новый диалог (модальный, чтобы блокировать главное окно)
        self.settings_dialog = SettingsDialog(self.settings, self)
        self.settings_dialog.setModal(True)
        if self.settings_dialog.exec():  # exec() блокирует, пока диалог не закроется
            self.recorder.update_settings()
            self.hotkey_manager.register_all(self.settings)
        # После закрытия сбрасываем ссылку
        self.settings_dialog = None

    @Slot()
    def on_recording_started(self):
        self.record_button.setText("Остановить запись")
        self.status_label.setText("Идет запись...")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.update_ui()

    @Slot(str)
    def on_recording_stopped(self, filepath):
        self.record_button.setText("Начать запись")
        self.status_label.setText("Готов")
        self.status_label.setStyleSheet("")
        if filepath:
            self.info_label.setText(f"Сохранено: {filepath}")
        self.update_ui()

    @Slot()
    def on_listening_started(self):
        self.status_label.setText("Прослушивание...")
        self.status_label.setStyleSheet("color: blue;")
        self.update_ui()

    @Slot()
    def on_listening_stopped(self):
        self.status_label.setText("Готов")
        self.status_label.setStyleSheet("")
        self.update_ui()

    @Slot(str)
    def on_status_message(self, msg):
        self.info_label.setText(msg)

    def update_ui(self):
        mode = "авто" if self.recorder.auto_mode else "ручной"
        self.mode_label.setText(f"Режим: {mode}")

    def closeEvent(self, event):
        self.recorder.cleanup()
        self.hotkey_manager.unregister_all()
        event.accept()