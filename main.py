import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app.core.constants import BASE_DIR
from app.database import init_db
from app.logger import logger
from app.ui import MainWindow
from app.utils.excel_parser import create_sample_files

def main():
    logger.info("Initializing TradePilot Desktop Application...")
    
    # 1. Initialize SQLite Database Schema
    init_db()

    # 2. Generate Sample Files in sample_data directory if needed
    sample_dir = BASE_DIR / "sample_data"
    create_sample_files(sample_dir)

    # 3. Start PySide6 QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("TradePilot")
    app.setOrganizationName("TradePilot")

    window = MainWindow()
    window.show()

    logger.info("TradePilot GUI launched successfully.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
