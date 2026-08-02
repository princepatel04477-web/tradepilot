from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton, QComboBox
from PySide6.QtGui import QTextCursor, QColor
from app.core.events import event_bus

class LogViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        event_bus.log_emitted.connect(self.append_log)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Control Bar
        ctrl_layout = QHBoxLayout()
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "INFO", "WARNING", "ERROR"])
        self.level_combo.setFixedWidth(100)

        clear_btn = QPushButton("Clear Output")
        clear_btn.setObjectName("SecondaryButton")
        clear_btn.setFixedWidth(110)
        clear_btn.clicked.connect(self.clear_logs)

        ctrl_layout.addWidget(self.level_combo)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(clear_btn)

        # Text Console
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("font-family: Consolas, 'Courier New', monospace; font-size: 12px; background-color: #11111B;")

        layout.addLayout(ctrl_layout)
        layout.addWidget(self.text_edit)

    def append_log(self, timestamp: str, level: str, message: str):
        filter_lvl = self.level_combo.currentText()
        if filter_lvl != "ALL" and level != filter_lvl:
            return

        color = "#CDD6F4"
        if level == "WARNING":
            color = "#F9E2AF"
        elif level == "ERROR":
            color = "#F38BA8"
        elif level == "SUCCESS" or "DRY_RUN" in message:
            color = "#A6E3A1"

        formatted = f'<span style="color: #6C7086;">[{timestamp}]</span> <b style="color: {color};">[{level}]</b> {message}'
        self.text_edit.append(formatted)
        self.text_edit.moveCursor(QTextCursor.End)

    def clear_logs(self):
        self.text_edit.clear()
