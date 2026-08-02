import os
import mimetypes
from pathlib import Path
from typing import List, Tuple
from app.models.template import AttachmentItem
from app.database.repository import Repository
from app.logger import logger

class AttachmentService:
    @staticmethod
    def register_attachment(filepath: str, category: str = "General") -> AttachmentItem:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        file_size = path.stat().st_size
        mime_type, _ = mimetypes.guess_type(str(path))
        if not mime_type:
            mime_type = "application/octet-stream"

        att = AttachmentItem(
            filename=path.name,
            filepath=str(path.resolve()),
            file_size_bytes=file_size,
            mime_type=mime_type,
            category=category
        )
        att.id = Repository.add_attachment(att)
        logger.info(f"Registered attachment '{att.filename}' ({round(file_size/1024, 1)} KB)")
        return att

    @staticmethod
    def get_all_attachments() -> List[AttachmentItem]:
        return Repository.get_attachments()

    @staticmethod
    def delete_attachment(att_id: int):
        Repository.delete_attachment(att_id)
