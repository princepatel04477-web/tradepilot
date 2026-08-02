from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AIServiceInterface(ABC):
    """Abstract extension point interface for AI personalization features."""

    @abstractmethod
    def generate_subject_line(self, company_name: str, product_desc: str) -> str:
        """Generate high-converting email subject lines."""
        pass

    @abstractmethod
    def rewrite_email(self, original_text: str, tone: str = "Professional") -> str:
        """Rewrite and refine email copy."""
        pass

    @abstractmethod
    def personalize_copy(self, template_str: str, contact_meta: Dict[str, Any]) -> str:
        """Company-specific AI email personalization."""
        pass

    @abstractmethod
    def calculate_spam_score(self, email_body: str) -> float:
        """Calculate deliverability & spam likelihood score (0.0 - 100.0)."""
        pass
