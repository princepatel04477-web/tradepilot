from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
)
from app.ui.components.log_viewer import LogViewerWidget
from app.services.export_service import ExportService

class LogsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Title & Export Button
        top_layout = QHBoxLayout()
        title_lbl = QLabel("System Activity & Email Dispatch Logs")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #CDD6F4;")

        export_btn = QPushButton("📊 Export Logs to CSV")
        export_btn.clicked.connect(self.export_csv)

        top_layout.addWidget(title_lbl)
        top_layout.addStretch()
        top_layout.addWidget(export_btn)
        layout.addLayout(top_layout)

        # Log Viewer Widget
        self.log_viewer = LogViewerWidget()
        layout.addWidget(self.log_viewer)

    def export_csv(self):
        try:
            filepath = ExportService.export_logs_to_csv()
            QMessageBox.information(self, "Export Complete", f"Logs exported to CSV:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
