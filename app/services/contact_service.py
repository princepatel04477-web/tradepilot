import csv
import re
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
        """Parses Excel or CSV file into Contact objects with multi-header detection, auto-email scanner, and headerless CSV support."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        df = None
        if path.suffix.lower() in [".xlsx", ".xls"]:
            try:
                df = pd.read_excel(filepath)
            except Exception as e:
                logger.error(f"Excel read error: {e}")
                try:
                    df = pd.read_excel(filepath, header=None)
                except Exception as ex2:
                    raise ValueError(f"Could not read Excel file: {e}")
        elif path.suffix.lower() == ".csv":
            try:
                df = pd.read_csv(filepath)
            except Exception as e:
                logger.warning(f"Pandas read_csv failed ({e}), trying utf-8-sig built-in fallback")
                try:
                    rows = []
                    with open(filepath, "r", encoding="utf-8-sig", errors="ignore") as f:
                        reader = csv.reader(f)
                        for r in reader:
                            rows.append(r)
                    df = pd.DataFrame(rows)
                except Exception as csv_err:
                    raise ValueError(f"Could not read CSV file: {csv_err}")
        else:
            # Fallback text reading
            try:
                with open(filepath, "r", encoding="utf-8-sig", errors="ignore") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip()]
                df = pd.DataFrame({"raw": lines})
            except Exception as txt_err:
                raise ValueError(f"Unsupported file format: {path.suffix}")

        if df is None or df.empty:
            return [], ["Uploaded file is empty."]

        # Check if first row/header itself is a valid email address (Headerless CSV scenario)
        email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        
        # Standardize column headers (case-insensitive strip)
        column_map = {}
        email_col_found = False

        for col in df.columns:
            cleaned = str(col).strip().lower()
            if cleaned in ["company", "company name", "organization", "company_name", "org"]:
                column_map[col] = "company"
            elif cleaned in ["contact", "contact name", "name", "full name", "person", "contact_name", "first_name", "last_name"]:
                column_map[col] = "contact_name"
            elif cleaned in ["email", "emails", "mail", "mails", "e-mail", "email address", "email_address", "email id", "email_id", "recipient", "recipients", "to", "contact_email", "contact email"]:
                column_map[col] = "email"
                email_col_found = True
            elif cleaned in ["country", "nation"]:
                column_map[col] = "country"
            elif cleaned in ["city", "town", "location"]:
                column_map[col] = "city"
            elif cleaned in ["phone", "phone number", "mobile", "tel"]:
                column_map[col] = "phone"

        # If header was not matched, check if any column header string IS an email (headerless file)
        header_emails = []
        for col in df.columns:
            col_str = str(col).strip().lower()
            if email_regex.match(col_str):
                header_emails.append(col_str)

        # Smart Email Column Discovery if header didn't match standard names
        if not email_col_found and not header_emails:
            # Scan each column to count valid email occurrences
            best_col = None
            max_email_count = 0
            for col in df.columns:
                count = 0
                for cell in df[col].dropna():
                    cell_str = str(cell).strip().lower()
                    if email_regex.match(cell_str):
                        count += 1
                if count > max_email_count:
                    max_email_count = count
                    best_col = col

            if best_col is not None:
                column_map[best_col] = "email"
                email_col_found = True

        df = df.rename(columns=column_map)

        valid_contacts: List[Contact] = []
        errors: List[str] = []
        seen_emails = set()

        # Include header emails if file was headerless
        for h_email in header_emails:
            if ValidationService.is_valid_email(h_email):
                seen_emails.add(h_email)
                valid_contacts.append(Contact(
                    company="", contact_name="", email=h_email, country="", city="", tags="Imported", status="Active"
                ))

        # Process all rows
        if "email" in df.columns:
            for idx, row in df.iterrows():
                row_num = idx + 2
                email_val = str(row.get("email", "")).strip() if pd.notna(row.get("email")) else ""

                if not email_val or email_val.lower() in ["nan", "none", "null"]:
                    continue

                # Extract email using regex if row contains text
                match = email_regex.search(email_val)
                if match:
                    email_normalized = match.group(0).lower()
                else:
                    # Search entire row string if cell wasn't exact match
                    row_str = " ".join([str(v) for v in row.values if pd.notna(v)])
                    matches = email_regex.findall(row_str)
                    if matches:
                        email_normalized = matches[0].lower()
                    else:
                        continue

                if email_normalized in seen_emails:
                    continue

                if not ValidationService.is_valid_email(email_normalized):
                    continue

                seen_emails.add(email_normalized)

                contact = Contact(
                    company=str(row.get("company", "")).strip() if pd.notna(row.get("company")) else "",
                    contact_name=str(row.get("contact_name", "")).strip() if pd.notna(row.get("contact_name")) else "",
                    email=email_normalized,
                    country=str(row.get("country", "")).strip() if pd.notna(row.get("country")) else "",
                    city=str(row.get("city", "")).strip() if pd.notna(row.get("city")) else "",
                    phone=str(row.get("phone", "")).strip() if pd.notna(row.get("phone")) else "",
                    tags="Imported",
                    status="Active"
                )
                valid_contacts.append(contact)

        # Fail-safe scanner if still no contacts found: scan entire file text for any email regex pattern
        if not valid_contacts:
            logger.info("Executing fail-safe text email scanner on uploaded file...")
            with open(filepath, "r", encoding="utf-8-sig", errors="ignore") as f:
                all_text = f.read()
            extracted_emails = set(email_regex.findall(all_text))
            for em in extracted_emails:
                em_clean = em.lower().strip()
                if ValidationService.is_valid_email(em_clean) and em_clean not in seen_emails:
                    seen_emails.add(em_clean)
                    valid_contacts.append(Contact(
                        company="", contact_name="", email=em_clean, country="", city="", tags="Imported", status="Active"
                    ))

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
