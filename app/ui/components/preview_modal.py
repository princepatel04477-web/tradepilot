from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPushButton, QListWidget, QFrame
)
from PySide6.QtCore import Qt

class EmailPreviewModal(QDialog):
    def __init__(self, recipient_email: str, subject: str, body_content: str, is_html: bool, attachments: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pre-flight Email Preview")
        self.resize(750, 600)
        self._init_ui(recipient_email, subject, body_content, is_html, attachments)

    def _init_ui(self, recipient_email: str, subject: str, body_content: str, is_html: bool, attachments: list):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header Info Card
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #181825; border-radius: 8px; padding: 12px;")
        header_layout = QVBoxLayout(header_frame)
        
        to_lbl = QLabel(f"<b>To:</b> {recipient_email}")
        to_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        subj_lbl = QLabel(f"<b>Subject:</b> {subject}")
        subj_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)

        header_layout.addWidget(to_lbl)
        header_layout.addWidget(subj_lbl)
        layout.addWidget(header_frame)

        # Body Preview Browser
        self.browser = QTextBrowser()
        self.browser.setStyleSheet("background-color: #11111B; border: 1px solid #313244; padding: 12px; color: #CDD6F4;")
        if is_html:
            self.browser.setHtml(body_content)
        else:
            self.browser.setPlainText(body_content)

        layout.addWidget(QLabel("<b>Rendered Body Preview:</b>"))
        layout.addWidget(self.browser)

        # Attachments Section
        if attachments:
            layout.addWidget(QLabel("<b>Attached Files:</b>"))
            att_list = QListWidget()
            att_list.setMaximumHeight(80)
            for a in attachments:
                size_kb = round(a.file_size_bytes / 1024, 1)
                att_list.addItem(f"📎 {a.filename} ({size_kb} KB) - {a.mime_type}")
            layout.addWidget(att_list)

        # Close Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close Preview")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
