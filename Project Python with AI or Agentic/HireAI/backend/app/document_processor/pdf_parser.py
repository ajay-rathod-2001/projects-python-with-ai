"""PDF Parser using PyMuPDF (fitz) with clean text extraction and fallback."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFParser:
    """Extracts raw text and structural metadata from PDF documents."""

    def extract_text(self, file_path: Path) -> str:
        """Read PDF file and return extracted plain text."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        extracted_pages = []

        # Try PyMuPDF (fitz)
        try:
            import fitz  # PyMuPDF

            with fitz.open(str(path)) as doc:
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text("text")
                    if text and text.strip():
                        extracted_pages.append(text.strip())

            if extracted_pages:
                full_text = "\n\n".join(extracted_pages)
                logger.info("Extracted %d characters across %d pages via PyMuPDF", len(full_text), len(extracted_pages))
                return full_text
        except Exception as e:
            logger.warning("PyMuPDF extraction failed or not available: %s. Trying fallback.", e)

        # Fallback to pdfplumber / pypdf if available
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            for page in reader.pages:
                text = page.extract_text()
                if text and text.strip():
                    extracted_pages.append(text.strip())

            if extracted_pages:
                return "\n\n".join(extracted_pages)
        except Exception as e:
            logger.warning("pypdf extraction fallback failed: %s", e)

        # Final fallback: binary string regex extraction for plain text streams
        try:
            with open(path, "rb") as f:
                content = f.read()
            import re
            text_chunks = re.findall(rb"\(([^\(\)\\]{3,})\)", content)
            if text_chunks:
                decoded = [c.decode("utf-8", errors="ignore") for c in text_chunks]
                return " ".join(decoded)
        except Exception as e:
            logger.error("Binary fallback failed: %s", e)

        return ""
