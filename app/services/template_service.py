import re
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
            rendered = template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            rendered = template_str
            for key, val in context.items():
                if isinstance(val, str):
                    rendered = rendered.replace(f"{{{{{key}}}}}", val)

        return rendered

    def render_html(self, template_str: str, contact: Contact) -> str:
        """Renders Jinja2 template and formats it into clean, structured HTML with proper paragraph spacing and bullet points."""
        text = self.render(template_str, contact)
        
        # If already full HTML document
        if "<html" in text.lower() or "<div" in text.lower() or "<p" in text.lower():
            return text

        # Convert text block to structured HTML
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        html_blocks = []

        for p in paragraphs:
            lines = p.split("\n")
            # Check if paragraph contains bullet points or list items
            if any(l.strip().startswith(("-", "*", "•")) for l in lines):
                list_items = []
                intro_lines = []
                for l in lines:
                    stripped = l.strip()
                    if stripped.startswith(("-", "*", "•")):
                        item_text = stripped.lstrip("-*• ").strip()
                        list_items.append(f'<li style="margin-bottom: 6px; font-family: Arial, sans-serif; color: #222222;">{item_text}</li>')
                    else:
                        intro_lines.append(l)
                
                block = ""
                if intro_lines:
                    block += f'<p style="margin-bottom: 8px; font-family: Arial, sans-serif; font-size: 14px; color: #222222; line-height: 1.6;">{"<br>".join(intro_lines)}</p>'
                if list_items:
                    block += f'<ul style="margin: 8px 0 16px 24px; padding: 0; list-style-type: disc;">{"".join(list_items)}</ul>'
                html_blocks.append(block)
            else:
                formatted_p = "<br>".join(lines)
                html_blocks.append(f'<p style="margin-bottom: 14px; font-family: Arial, sans-serif; font-size: 14px; color: #222222; line-height: 1.6;">{formatted_p}</p>')

        full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: Arial, sans-serif; font-size: 14px; color: #222222; line-height: 1.6; background-color: #ffffff; margin: 0; padding: 20px; }}
p {{ margin-bottom: 14px; line-height: 1.6; }}
ul {{ margin: 8px 0 16px 24px; padding: 0; }}
li {{ margin-bottom: 6px; }}
</style>
</head>
<body>
<div style="max-width: 650px; margin: 0 auto; background: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0;">
{"".join(html_blocks)}
</div>
</body>
</html>"""
        return full_html

    def validate_template_syntax(self, template_str: str) -> Tuple[bool, str]:
        try:
            self.jinja_env.from_string(template_str)
            return True, "Syntax valid"
        except TemplateSyntaxError as e:
            return False, f"Syntax Error at line {e.lineno}: {e.message}"
        except Exception as e:
            return False, str(e)

template_service = TemplateService()
