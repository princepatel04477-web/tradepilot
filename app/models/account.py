from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class GmailAccount:
    id: Optional[int] = None
    email: str = ""
    display_name: str = ""
    refresh_token_encrypted: str = ""
    is_active: bool = True
    sent_today_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
