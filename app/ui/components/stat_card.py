from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class StatCard(QFrame):
    def __init__(self, title: str, initial_value: str = "0", accent_color: str = "#89B4FA", parent=None):
        super().__init__(parent)
        self.setProperty("class", "StatCard")
        self.accent_color = accent_color
        self._init_ui(title, initial_value)

    def _init_ui(self, title: str, initial_value: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #A6ADC8; font-size: 12px; font-weight: 600; text-transform: uppercase;")

        self.value_label = QLabel(initial_value)
        self.value_label.setStyleSheet(f"color: {self.accent_color}; font-size: 26px; font-weight: bold;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str):
        self.value_label.setText(str(value))
