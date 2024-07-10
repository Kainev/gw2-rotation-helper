from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPainter, QColor, Qt
from PySide6.QtCore import QRect

from core.constants import ACTION_HIGHLIGHTS


class ActionHighlighter(QWidget):
    def __init__(self, action, screen, label, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setFixedSize(screen[2], screen[3])
        self.move(screen[0], screen[1])

        self._highlight = ACTION_HIGHLIGHTS[action] if action else [0, 0, 0, 0]

        self._sequence_label = QLabel(self)
        self._sequence_label.setText(label)
        self._sequence_label.setStyleSheet("width: 100px; background-color: rgba(0, 0, 0, 128); border: 2px solid rgba(0, 255, 0, 20); color: rgba(255, 255, 255, 200); padding: 8px; font-weight: bold; text-align: center")

        # self._sequence_label.move(1229, 1225)  # Position at top-left, adjust as needed
        self._sequence_label.setAlignment(Qt.AlignCenter)

        normalized_width_difference = 100 - self._sequence_label.width()
        self._sequence_label.move(807 - normalized_width_difference, 1366)  # Position at top-left, adjust as needed
        self._sequence_label.setMinimumWidth(100)

        self.show()
        self.hide()

    @property
    def highlight(self):
        return self._highlight

    @highlight.setter
    def highlight(self, action):
        self._highlight = ACTION_HIGHLIGHTS[action]
        self.update()

    @property
    def label(self):
        return self._sequence_label.text()

    @label.setter
    def label(self, label):
        self._sequence_label.setText(label)
        self._sequence_label.adjustSize()
        normalized_width_difference = 100 - self._sequence_label.width()
        self._sequence_label.move(807 + normalized_width_difference, 1366)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(0, 0, 255, 128))
        painter.setPen(QColor(0, 0, 0, 0))  # Set the stroke color to blue

        rect = QRect(*self._highlight)
        painter.drawRect(rect)

