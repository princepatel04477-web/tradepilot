from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QButtonGroup
from PySide6.QtCore import Signal, Qt

class Sidebar(QWidget):
    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarWidget")
        self.setFixedWidth(220)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)

        # App Brand Header
        brand_label = QLabel("✈ TradePilot")
        brand_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #89B4FA; margin-bottom: 20px; margin-left: 8px;")
        layout.addWidget(brand_label)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        pages = [
            ("📊 Dashboard", 0),
            ("🚀 Campaigns", 1),
            ("👥 Contacts", 2),
            ("📝 Templates", 3),
            ("📎 Attachments", 4),
            ("🔑 Gmail Accounts", 5),
            ("📋 Logs", 6),
            ("⚙ Settings", 7)
        ]

        for text, index in pages:
            btn = QPushButton(text)
            btn.setCheckable(True)
            if index == 0:
                btn.setChecked(True)
            self.button_group.addButton(btn, index)
            layout.addWidget(btn)

        self.button_group.idClicked.connect(self.page_changed.emit)
        layout.addStretch()

        # Footer Version Label
        version_label = QLabel("v1.0.0 Enterprise")
        version_label.setStyleSheet("color: #6C7086; font-size: 11px; margin-left: 8px;")
        layout.addWidget(version_label)
