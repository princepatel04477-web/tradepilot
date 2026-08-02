from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd
from app.models.contact import Contact
from app.services.validation_service import ValidationService
from app.database.repository import Repository
from app.logger import logger

class ContactService:
    @staticmethod
    def parse_import_file(filepath: str) -> Tuple[List[Contact], List[str]]:
        """Parses Excel or CSV file into Contact objects with validation and deduplication."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        if path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(filepath)
        elif path.suffix.lower() == ".csv":
            df = pd.read_csv(filepath)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}. Must be .xlsx, .xls, or .csv")

        # Standardize column headers (case-insensitive strip)
        column_map = {}
        for col in df.columns:
            cleaned = str(col).strip().lower()
            if cleaned in ["company", "company name", "organization"]:
                column_map[col] = "company"
            elif cleaned in ["contact", "contact name", "name", "full name", "person"]:
                column_map[col] = "contact_name"
            elif cleaned in ["email", "e-mail", "email address"]:
                column_map[col] = "email"
            elif cleaned in ["country", "nation"]:
                column_map[col] = "country"
            elif cleaned in ["city", "town", "location"]:
                column_map[col] = "city"
            elif cleaned in ["phone", "phone number", "mobile", "tel"]:
                column_map[col] = "phone"
            elif cleaned in ["tags", "tag"]:
                column_map[col] = "tags"
            elif cleaned in ["status"]:
                column_map[col] = "status"

        df = df.rename(columns=column_map)

        valid_contacts: List[Contact] = []
        errors: List[str] = []
        seen_emails = set()

        for idx, row in df.iterrows():
            row_num = idx + 2  # 1-indexed header + 1
            email_val = str(row.get("email", "")).strip() if pd.notna(row.get("email")) else ""

            if not email_val or email_val.lower() == "nan":
                errors.append(f"Row {row_num}: Missing email address.")
                continue

            email_normalized = email_val.lower()
            if email_normalized in seen_emails:
                errors.append(f"Row {row_num}: Duplicate email within file ({email_val}). Skipped.")
                continue

            if not ValidationService.is_valid_email(email_normalized):
                errors.append(f"Row {row_num}: Invalid email format ({email_val}). Skipped.")
                continue

            seen_emails.add(email_normalized)

            # Custom fields parsing
            standard_cols = {"company", "contact_name", "email", "country", "city", "phone", "tags", "status"}
            custom_fields = {}
            for col in df.columns:
                mapped_name = column_map.get(col, col)
                if mapped_name not in standard_cols and pd.notna(row[col]):
                    custom_fields[str(col)] = str(row[col])

            contact = Contact(
                company=str(row.get("company", "")).strip() if pd.notna(row.get("company")) else "",
                contact_name=str(row.get("contact_name", "")).strip() if pd.notna(row.get("contact_name")) else "",
                email=email_normalized,
                country=str(row.get("country", "")).strip() if pd.notna(row.get("country")) else "",
                city=str(row.get("city", "")).strip() if pd.notna(row.get("city")) else "",
                phone=str(row.get("phone", "")).strip() if pd.notna(row.get("phone")) else "",
                tags=str(row.get("tags", "")).strip() if pd.notna(row.get("tags")) else "Imported",
                status=str(row.get("status", "Active")).strip() if pd.notna(row.get("status")) else "Active",
                custom_fields=custom_fields
            )
            valid_contacts.append(contact)

        return valid_contacts, errors

    @staticmethod
    def import_contacts_to_db(filepath: str) -> Dict[str, Any]:
        contacts, errors = ContactService.parse_import_file(filepath)
        inserted_count = Repository.add_contacts_batch(contacts)
        logger.info(f"Imported {inserted_count} new contacts from {filepath} ({len(errors)} warnings).")
        return {
            "total_parsed": len(contacts),
            "inserted": inserted_count,
            "duplicates_skipped": len(contacts) - inserted_count,
            "errors": errors
        }
