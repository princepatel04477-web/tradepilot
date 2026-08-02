from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QSpinBox,
    QDoubleSpinBox, QPushButton, QMessageBox, QFileDialog, QFrame
)
from app.core.config import config
from app.core.constants import DEFAULT_DB_PATH

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title_lbl = QLabel("Application Settings & Configuration")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #CDD6F4;")
        layout.addWidget(title_lbl)

        frame = QFrame()
        frame.setStyleSheet("background-color: #181825; border-radius: 8px; padding: 20px;")
        frame_box = QVBoxLayout(frame)
        frame_box.setSpacing(12)

        # Default Sender & Signature
        self.sender_input = QLineEdit()
        self.sender_input.setText(config.get("sender.default_sender", ""))
        self.sender_input.setPlaceholderText("Default Sender (e.g. Export Team <sales@company.com>)")

        self.signature_input = QTextEdit()
        self.signature_input.setText(config.get("sender.default_signature", ""))

        # Delays & Limits
        delay_box = QHBoxLayout()
        delay_box.addWidget(QLabel("Default Min Delay (sec):"))
        self.min_delay_sp = QDoubleSpinBox()
        self.min_delay_sp.setValue(config.get("campaign_defaults.min_delay_sec", 30.0))
        delay_box.addWidget(self.min_delay_sp)

        delay_box.addWidget(QLabel("Default Max Delay (sec):"))
        self.max_delay_sp = QDoubleSpinBox()
        self.max_delay_sp.setValue(config.get("campaign_defaults.max_delay_sec", 60.0))
        delay_box.addWidget(self.max_delay_sp)

        delay_box.addWidget(QLabel("Daily Send Limit:"))
        self.limit_sp = QSpinBox()
        self.limit_sp.setRange(1, 10000)
        self.limit_sp.setValue(config.get("campaign_defaults.daily_send_limit", 500))
        delay_box.addWidget(self.limit_sp)

        # Database Path
        db_box = QHBoxLayout()
        self.db_input = QLineEdit()
        self.db_input.setText(config.get("database.sqlite_path", str(DEFAULT_DB_PATH)))
        browse_db_btn = QPushButton("Browse...")
        browse_db_btn.setObjectName("SecondaryButton")
        browse_db_btn.clicked.connect(self.browse_db)
        db_box.addWidget(self.db_input)
        db_box.addWidget(browse_db_btn)

        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)

        frame_box.addWidget(QLabel("Default Sender:"))
        frame_box.addWidget(self.sender_input)
        frame_box.addWidget(QLabel("Default Signature:"))
        frame_box.addWidget(self.signature_input)
        frame_box.addLayout(delay_box)
        frame_box.addWidget(QLabel("SQLite Database Location:"))
        frame_box.addLayout(db_box)
        frame_box.addStretch()
        frame_box.addWidget(save_btn)

        layout.addWidget(frame)

    def browse_db(self):
        fp, _ = QFileDialog.getSaveFileName(self, "Select Database Location", str(DEFAULT_DB_PATH), "SQLite Database (*.db)")
        if fp:
            self.db_input.setText(fp)

    def save_settings(self):
        config.set("sender.default_sender", self.sender_input.text().strip())
        config.set("sender.default_signature", self.signature_input.toPlainText().strip())
        config.set("campaign_defaults.min_delay_sec", self.min_delay_sp.value())
        config.set("campaign_defaults.max_delay_sec", self.max_delay_sp.value())
        config.set("campaign_defaults.daily_send_limit", self.limit_sp.value())
        config.set("database.sqlite_path", self.db_input.text().strip())
        QMessageBox.information(self, "Saved", "Settings updated successfully.")
