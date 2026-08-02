from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class LogEntry:
    id: Optional[int] = None
    campaign_id: Optional[int] = None
    recipient_email: str = ""
    status: str = "INFO"
    log_level: str = "INFO"
    details: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
