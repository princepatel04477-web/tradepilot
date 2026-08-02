from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class CampaignRecipient:
    id: Optional[int] = None
    campaign_id: int = 0
    contact_id: int = 0
    status: str = "PENDING"  # PENDING, SENT, FAILED, SKIPPED
    message_id: Optional[str] = None
    sent_at: Optional[str] = None
    error_reason: Optional[str] = None
    retry_count: int = 0

@dataclass
class Campaign:
    id: Optional[int] = None
    name: str = ""
    account_id: Optional[int] = None
    template_id: Optional[int] = None
    status: str = "DRAFT"  # DRAFT, QUEUED, RUNNING, PAUSED, COMPLETED, CANCELLED
    min_delay_sec: float = 30.0
    max_delay_sec: float = 60.0
    daily_limit: int = 500
    is_dry_run: bool = True
    subject_override: Optional[str] = None
    attachment_ids: List[int] = field(default_factory=list)
    total_recipients: int = 0
    sent_count: int = 0
    failed_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
