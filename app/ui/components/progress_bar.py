from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel

class CampaignProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        info_layout = QHBoxLayout()
        self.status_label = QLabel("Campaign Queue Idle")
        self.status_label.setStyleSheet("color: #CDD6F4; font-weight: 600;")
        
        self.eta_label = QLabel("ETA: --:--")
        self.eta_label.setStyleSheet("color: #A6ADC8;")

        info_layout.addWidget(self.status_label)
        info_layout.addStretch()
        info_layout.addWidget(self.eta_label)

        self.bar = QProgressBar()
        self.bar.setFixedHeight(22)
        self.bar.setValue(0)

        layout.addLayout(info_layout)
        layout.addWidget(self.bar)

    def update_progress(self, processed: int, total: int, current_email: str, eta_sec: int):
        pct = int((processed / total * 100)) if total > 0 else 0
        self.bar.setValue(pct)
        self.status_label.setText(f"Processing ({processed}/{total}): {current_email}")

        mins, secs = divmod(eta_sec, 60)
        hrs, mins = divmod(mins, 60)
        if hrs > 0:
            eta_str = f"{hrs}h {mins}m {secs}s"
        else:
            eta_str = f"{mins}m {secs}s"
        self.eta_label.setText(f"ETA: {eta_str}")

    def reset(self, status_text: str = "Ready"):
        self.bar.setValue(0)
        self.status_label.setText(status_text)
        self.eta_label.setText("ETA: --:--")
