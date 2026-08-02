import re

def clean_phone_number(phone: str) -> str:
    if not phone:
        return ""
    return re.sub(r"[^\d\+\-\s\(\)]", "", str(phone)).strip()

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", str(filename)).strip()
