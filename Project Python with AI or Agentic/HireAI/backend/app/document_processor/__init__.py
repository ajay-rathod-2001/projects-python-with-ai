"""Document Processor Package for multi-format text extraction."""

import logging
from pathlib import Path
from app.document_processor.pdf_parser import PDFParser
from app.document_processor.docx_parser import DOCXParser
from app.document_processor.txt_parser import TXTParser
from app.document_processor.rtf_parser import RTFParser

logger = logging.getLogger(__name__)

pdf_parser = PDFParser()
docx_parser = DOCXParser()
txt_parser = TXTParser()
rtf_parser = RTFParser()


def extract_document_text(file_path: Path, file_format: str) -> str:
    """Extract clean text from a document based on its extension or format.

    Args:
        file_path: Absolute or relative Path to the file.
        file_format: File extension without leading dot (e.g. 'pdf', 'docx', 'txt', 'rtf').

    Returns:
        Extracted plain text normalized.
    """
    fmt = file_format.lower().strip().lstrip(".")
    path = Path(file_path)

    text = ""
    try:
        if fmt == "pdf":
            text = pdf_parser.extract_text(path)
        elif fmt in ("docx", "doc"):
            # For docx
            try:
                text = docx_parser.extract_text(path)
            except Exception:
                text = txt_parser.extract_text(path)
        elif fmt == "rtf":
            text = rtf_parser.extract_text(path)
        elif fmt in ("txt", "md"):
            text = txt_parser.extract_text(path)
        else:
            # Fallback to plain text reader
            text = txt_parser.extract_text(path)
    except Exception as e:
        logger.error("Error extracting text from %s (%s): %s", path, fmt, e)
        # Final emergency fallback
        try:
            text = txt_parser.extract_text(path)
        except Exception:
            text = ""

    # Clean and normalize text
    if text:
        # Normalize carriage returns and excessive whitespace
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

    return text.strip()


__all__ = [
    "PDFParser",
    "DOCXParser",
    "TXTParser",
    "RTFParser",
    "extract_document_text",
]
