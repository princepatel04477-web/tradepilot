import os
import yaml
from pathlib import Path
from app.core.constants import DEFAULT_CONFIG_PATH, DEFAULT_DB_PATH

class ConfigManager:
    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH):
        self.config_path = config_path
        self._config = {}
        self.load()

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception:
                self._config = self._get_defaults()
        else:
            self._config = self._get_defaults()
            self.save()

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._config, f, default_flow_style=False)

    def _get_defaults(self) -> dict:
        return {
            "app": {"name": "TradePilot", "version": "1.0.0", "theme": "dark"},
            "sender": {"default_sender": "", "default_signature": "Best regards,\nTradePilot Team"},
            "campaign_defaults": {
                "min_delay_sec": 30,
                "max_delay_sec": 60,
                "daily_send_limit": 500,
                "retry_attempts": 3,
                "dry_run_default": True
            },
            "database": {"sqlite_path": str(DEFAULT_DB_PATH)},
            "paths": {"logs_dir": "logs", "exports_dir": "exports", "campaigns_dir": "campaigns"}
        }

    def get(self, key_path: str, default=None):
        keys = key_path.split(".")
        val = self._config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key_path: str, value):
        keys = key_path.split(".")
        target = self._config
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self.save()

# Global config singleton
config = ConfigManager()
