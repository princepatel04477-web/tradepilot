import re
from pathlib import Path
from typing import List, Tuple, Dict, Any
from email_validator import validate_email, EmailNotValidError
from app.logger import logger

class ValidationService:
    MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB Gmail limit

    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not email or not isinstance(email, str):
            return False
        try:
            validate_email(email.strip(), check_deliverability=False)
            return True
        except EmailNotValidError:
            return False

    @staticmethod
    def validate_contact(data: dict) -> Tuple[bool, str]:
        email = data.get("email", "").strip()
        if not email:
            return False, "Email is required"
        if not ValidationService.is_valid_email(email):
            return False, f"Invalid email format: {email}"
        return True, ""

    @staticmethod
    def validate_attachments_total_size(filepaths: List[str]) -> Tuple[bool, str]:
        total_bytes = 0
        for fp in filepaths:
            p = Path(fp)
            if p.exists():
                total_bytes += p.stat().st_size
            else:
                return False, f"Attachment file not found: {fp}"
        
        if total_bytes > ValidationService.MAX_ATTACHMENT_SIZE_BYTES:
            mb_size = round(total_bytes / (1024 * 1024), 2)
            return False, f"Total attachments size ({mb_size} MB) exceeds maximum Gmail limit of 25 MB."
        return True, ""

    @staticmethod
    def extract_template_variables(text: str) -> List[str]:
        """Extracts variables in format {{Variable}} or {{Custom.Variable}}."""
        if not text:
            return []
        pattern = r"\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}"
        matches = re.findall(pattern, text)
        return list(set(matches))
