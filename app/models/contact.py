import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class Contact:
    id: Optional[int] = None
    company: str = ""
    contact_name: str = ""
    email: str = ""
    country: str = ""
    city: str = ""
    phone: str = ""
    tags: str = ""
    status: str = "Active"
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def custom_fields_json(self) -> str:
        return json.dumps(self.custom_fields)

    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        custom = data.get("custom_fields", {})
        if isinstance(custom, str):
            try:
                custom = json.loads(custom)
            except Exception:
                custom = {}
        return cls(
            id=data.get("id"),
            company=data.get("company", ""),
            contact_name=data.get("contact_name", ""),
            email=data.get("email", ""),
            country=data.get("country", ""),
            city=data.get("city", ""),
            phone=data.get("phone", ""),
            tags=data.get("tags", ""),
            status=data.get("status", "Active"),
            custom_fields=custom,
            created_at=data.get("created_at", datetime.now().isoformat())
        )
