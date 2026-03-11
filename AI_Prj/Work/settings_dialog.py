from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget,
                               QFormLayout, QSpinBox, QLineEdit, QDialogButtonBox)
from widgets import HotkeyEdit

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Общие
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        tabs.addTab(general_tab, "Общие")

        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 5000)
        self.threshold_spin.setSuffix(" RMS")
        general_layout.addRow("Порог громкости:", self.threshold_spin)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setSuffix(" сек")
        general_layout.addRow("Таймаут тишины:", self.timeout_spin)

        self.output_dir_edit = QLineEdit()
        general_layout.addRow("Папка записей:", self.output_dir_edit)

        # Хоткеи
        hotkey_tab = QWidget()
        hotkey_layout = QFormLayout(hotkey_tab)
        tabs.addTab(hotkey_tab, "Хоткеи")

        self.hotkey_record_edit = HotkeyEdit()
        hotkey_layout.addRow("Старт/стоп записи:", self.hotkey_record_edit)

        self.hotkey_auto_edit = HotkeyEdit()
        hotkey_layout.addRow("Переключить авторежим:", self.hotkey_auto_edit)

        self.hotkey_settings_edit = HotkeyEdit()
        hotkey_layout.addRow("Открыть настройки:", self.hotkey_settings_edit)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_settings(self):
        self.threshold_spin.setValue(self.settings.silence_threshold)
        self.timeout_spin.setValue(self.settings.silence_timeout)
        self.output_dir_edit.setText(self.settings.output_dir)
        self.hotkey_record_edit.setText(self.settings.hotkey_toggle_record)
        self.hotkey_auto_edit.setText(self.settings.hotkey_toggle_auto)
        self.hotkey_settings_edit.setText(self.settings.hotkey_settings)

    def accept(self):
        self.settings.silence_threshold = self.threshold_spin.value()
        self.settings.silence_timeout = self.timeout_spin.value()
        self.settings.output_dir = self.output_dir_edit.text()
        self.settings.hotkey_toggle_record = self.hotkey_record_edit.text()
        self.settings.hotkey_toggle_auto = self.hotkey_auto_edit.text()
        self.settings.hotkey_settings = self.hotkey_settings_edit.text()
        self.settings.save()
        super().accept()