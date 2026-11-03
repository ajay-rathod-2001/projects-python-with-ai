"""Plain text parser with encoding detection via chardet and robust fallbacks."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TXTParser:
    """Reads plain text files with automatic character encoding detection."""

    def extract_text(self, file_path: Path) -> str:
        """Detect encoding (UTF-8, Latin-1, Windows-1252, etc.) and return decoded text."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Text file not found: {path}")

        raw_bytes = path.read_bytes()
        if not raw_bytes:
            return ""

        # Try chardet first
        try:
            import chardet

            detection = chardet.detect(raw_bytes[:8192])
            encoding = detection.get("encoding")
            if encoding:
                try:
                    return raw_bytes.decode(encoding)
                except Exception:
                    pass
        except Exception:
            pass

        # Try standard encodings sequentially
        for enc in ("utf-8", "utf-8-sig", "windows-1252", "latin-1", "ascii"):
            try:
                return raw_bytes.decode(enc)
            except UnicodeDecodeError:
                continue

        # Fallback with ignore errors
        return raw_bytes.decode("utf-8", errors="ignore")
