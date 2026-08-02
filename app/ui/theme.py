DARK_THEME_QSS = """
/* TradePilot Professional Dark Theme QSS */

QWidget {
    background-color: #1E1E2E;
    color: #CDD6F4;
    font-family: "Segoe UI", "Roboto", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #181825;
}

/* Sidebar Styling */
#SidebarWidget {
    background-color: #11111B;
    border-right: 1px solid #313244;
}

#SidebarWidget QPushButton {
    background-color: transparent;
    color: #A6ADC8;
    text-align: left;
    padding: 12px 16px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
}

#SidebarWidget QPushButton:hover {
    background-color: #1E1E2E;
    color: #CDD6F4;
}

#SidebarWidget QPushButton:checked {
    background-color: #313244;
    color: #89B4FA;
    font-weight: bold;
}

/* Card Widget */
.StatCard {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 10px;
    padding: 16px;
}

/* Buttons */
QPushButton {
    background-color: #89B4FA;
    color: #11111B;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}

QPushButton:hover {
    background-color: #B4BEFE;
}

QPushButton:pressed {
    background-color: #74C7EC;
}

QPushButton#DangerButton {
    background-color: #F38BA8;
    color: #11111B;
}

QPushButton#DangerButton:hover {
    background-color: #EBA0AC;
}

QPushButton#SecondaryButton {
    background-color: #313244;
    color: #CDD6F4;
}

QPushButton#SecondaryButton:hover {
    background-color: #45475A;
}

/* Input Controls */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #181825;
    border: 1px solid #45475A;
    border-radius: 6px;
    padding: 8px;
    color: #CDD6F4;
    selection-background-color: #585B70;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #89B4FA;
}

/* Tables */
QTableWidget {
    background-color: #181825;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 8px;
    selection-background-color: #45475A;
    selection-color: #CDD6F4;
}

QHeaderView::section {
    background-color: #11111B;
    color: #BAC2DE;
    padding: 8px;
    border: none;
    font-weight: bold;
}

/* Progress Bar */
QProgressBar {
    background-color: #313244;
    border-radius: 6px;
    text-align: center;
    color: #CDD6F4;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #A6E3A1;
    border-radius: 6px;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #181825;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #45475A;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585B70;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #1E1E2E;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #181825;
    color: #A6ADC8;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #313244;
    color: #89B4FA;
    font-weight: bold;
}
"""
