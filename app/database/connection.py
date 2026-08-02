import sqlite3
import threading
from pathlib import Path
from typing import Optional
from app.core.config import config
from app.core.constants import DEFAULT_DB_PATH

class DatabaseConnection:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.get("database.sqlite_path", str(DEFAULT_DB_PATH))
        self._lock = threading.Lock()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Enable Write-Ahead Logging for concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def execute_script(self, sql_script: str):
        with self._lock:
            with self.get_connection() as conn:
                conn.executescript(sql_script)
                conn.commit()

# Global database manager
db_manager = DatabaseConnection()
