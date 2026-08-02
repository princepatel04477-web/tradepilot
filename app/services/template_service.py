from typing import Dict, Any, List, Tuple
from jinja2 import Environment, BaseLoader, TemplateSyntaxError, UndefinedError
from app.models.contact import Contact
from app.models.template import EmailTemplate
from app.services.validation_service import ValidationService
from app.logger import logger

class TemplateService:
    def __init__(self):
        self.jinja_env = Environment(loader=BaseLoader(), autoescape=False)

    def extract_variables(self, content: str) -> List[str]:
        return ValidationService.extract_template_variables(content)

    def render(self, template_str: str, contact: Contact) -> str:
        """Renders Jinja2 template string with contact data dictionary."""
        context = {
            "Company": contact.company or "Valued Client",
            "Contact": contact.contact_name or "Partner",
            "Email": contact.email,
            "Country": contact.country or "Global",
            "City": contact.city or "City",
            "Phone": contact.phone or "",
            "Custom": contact.custom_fields or {}
        }
        # Also expose lower-case keys for convenience
        context["company"] = context["Company"]
        context["contact"] = context["Contact"]
        context["email"] = context["Email"]
        context["country"] = context["Country"]
        context["city"] = context["City"]

        try:
            template = self.jinja_env.from_string(template_str)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            # Fallback simple string replacement if Jinja fails
            res = template_str
            for key, val in context.items():
                if isinstance(val, str):
                    res = res.replace(f"{{{{{key}}}}}", val)
            return res

    def validate_template_syntax(self, template_str: str) -> Tuple[bool, str]:
        try:
            self.jinja_env.from_string(template_str)
            return True, "Syntax valid"
        except TemplateSyntaxError as e:
            return False, f"Syntax Error at line {e.lineno}: {e.message}"
        except Exception as e:
            return False, str(e)

template_service = TemplateService()
