import keyboard
from PySide6.QtCore import QObject, Signal

class HotkeyManager(QObject):
    toggle_record = Signal()
    toggle_auto = Signal()
    open_settings = Signal()

    def __init__(self):
        super().__init__()
        self.registered_hotkeys = {}

    def register_all(self, settings):
        self.unregister_all()
        if settings.hotkey_toggle_record:
            self._register(settings.hotkey_toggle_record, self.toggle_record)
        if settings.hotkey_toggle_auto:
            self._register(settings.hotkey_toggle_auto, self.toggle_auto)
        if settings.hotkey_settings:
            self._register(settings.hotkey_settings, self.open_settings)

    def _register(self, combo, signal):
        try:
            def callback():
                signal.emit()
            keyboard.add_hotkey(combo, callback)
            self.registered_hotkeys[combo] = callback
        except Exception as e:
            print(f"Не удалось зарегистрировать хоткей {combo}: {e}")

    def unregister_all(self):
        keyboard.unhook_all()
        self.registered_hotkeys.clear()