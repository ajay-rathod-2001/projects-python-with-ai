"""RTF (Rich Text Format) Parser using striprtf with regex fallback."""

import logging
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class RTFParser:
    """Strips formatting controls from RTF documents and returns clean text."""

    def extract_text(self, file_path: Path) -> str:
        """Strip RTF tags and return extracted text."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"RTF file not found: {path}")

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            content = path.read_bytes().decode("latin-1", errors="ignore")

        # Try striprtf
        try:
            from striprtf.striprtf import rtf_to_text

            clean_text = rtf_to_text(content)
            if clean_text and clean_text.strip():
                return clean_text.strip()
        except Exception as e:
            logger.warning("striprtf failed: %s. Using regex fallback.", e)

        # Regex fallback to strip rtf control sequences
        pattern = re.compile(r"\\[a-zA-Z0-9\-]+ ?|[{}\\]")
        cleaned = pattern.sub(" ", content)
        return re.sub(r"\s+", " ", cleaned).strip()
