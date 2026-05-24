from __future__ import annotations

import re
from pathlib import Path

from config import settings
from database.mongodb import mongo
from services.chromadb_service import chromadb_service
from utils.text import chunk_plain_text


class DocumentService:
    supported_types = {"pdf", "txt", "md", "docx"}

    def ingest(self, uploaded_file, user_id: str) -> str:
        suffix = Path(uploaded_file.name).suffix.lower().lstrip(".")
        if suffix not in self.supported_types:
            raise ValueError("Supported document types are PDF, TXT, MD, and DOCX.")

        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", uploaded_file.name)
        file_path = settings.upload_path / safe_name
        file_path.write_bytes(uploaded_file.getbuffer())

        text = self.extract_text(file_path)
        if not text.strip():
            raise ValueError("No readable text was found in this document.")

        chunks = chunk_plain_text(text)
        source = {
            "user_id": user_id,
            "youtube_url": "",
            "youtube_id": "",
            "source_type": "document",
            "file_name": uploaded_file.name,
            "file_path": str(file_path),
            "title": Path(uploaded_file.name).stem,
            "status": "ready",
        }
        existing = mongo.find_one("videos", {"user_id": user_id, "file_name": uploaded_file.name, "source_type": "document"})
        video_id = str(existing["_id"]) if existing else mongo.insert("videos", source)
        if existing:
            mongo.update("videos", {"_id": video_id}, {"$set": source})

        mongo.upsert(
            "transcripts",
            {"video_id": video_id},
            {"video_id": video_id, "source": f"document:{suffix}", "text": text, "chunks": chunks},
        )
        chromadb_service.upsert_chunks(video_id, chunks)
        return video_id

    def extract_text(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf(path)
        if suffix == ".docx":
            return self._extract_docx(path)
        return path.read_text(encoding="utf-8", errors="ignore")

    def _extract_pdf(self, path: Path) -> str:
        try:
            from pypdf import PdfReader
        except Exception as exc:
            raise RuntimeError("Install pypdf to read PDF files.") from exc
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _extract_docx(self, path: Path) -> str:
        try:
            from docx import Document
        except Exception as exc:
            raise RuntimeError("Install python-docx to read DOCX files.") from exc
        doc = Document(str(path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)


document_service = DocumentService()
