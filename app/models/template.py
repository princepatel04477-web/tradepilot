import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class EmailTemplate:
    id: Optional[int] = None
    name: str = ""
    subject: str = ""
    body_content: str = ""
    is_html: bool = True
    variables: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def variables_json(self) -> str:
        return json.dumps(self.variables)

@dataclass
class AttachmentItem:
    id: Optional[int] = None
    filename: str = ""
    filepath: str = ""
    file_size_bytes: int = 0
    mime_type: str = ""
    category: str = "General"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
