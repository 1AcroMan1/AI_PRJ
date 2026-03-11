from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeySequence

class HotkeyEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Нажмите комбинацию...")
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            # Игнорируем одиночные модификаторы
            if event.key() in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
                return True
            mods = event.modifiers()
            key = event.key()
            keys = []
            if mods & Qt.ControlModifier:
                keys.append("ctrl")
            if mods & Qt.ShiftModifier:
                keys.append("shift")
            if mods & Qt.AltModifier:
                keys.append("alt")
            if mods & Qt.MetaModifier:
                keys.append("win")
            key_name = QKeySequence(key).toString().toLower()
            if key_name:
                keys.append(key_name)
            self.setText("+".join(keys))
            return True
        return super().eventFilter(obj, event)