"""DOCX Parser using python-docx with paragraph and table extraction."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DOCXParser:
    """Extracts paragraphs, headings, and table cells from DOCX documents."""

    def extract_text(self, file_path: Path) -> str:
        """Read DOCX file and return extracted plain text."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"DOCX file not found: {path}")

        extracted_lines = []

        try:
            import docx

            doc = docx.Document(str(path))
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    extracted_lines.append(text)

            # Also extract from tables
            for table in doc.tables:
                for row in table.rows:
                    row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_texts:
                        extracted_lines.append(" | ".join(row_texts))

            if extracted_lines:
                return "\n".join(extracted_lines)
        except Exception as e:
            logger.warning("python-docx extraction failed: %s. Trying zipfile xml fallback.", e)

        # Fallback using zipfile to extract word/document.xml directly without docx
        try:
            import xml.etree.ElementTree as ET
            import zipfile

            with zipfile.ZipFile(str(path)) as zf:
                xml_content = zf.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            # Find all text tags
            texts = [node.text for node in tree.iter() if node.text]
            return " ".join(texts)
        except Exception as e:
            logger.error("XML fallback failed: %s", e)

        return ""
