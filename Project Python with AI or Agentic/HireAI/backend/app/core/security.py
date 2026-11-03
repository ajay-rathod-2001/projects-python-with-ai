"""Security controls, path traversal prevention, and input sanitization."""

import os
from pathlib import Path
import re


def sanitize_filename(filename: str) -> str:
    """Strip dangerous characters and path traversal indicators from filename."""
    clean_name = os.path.basename(filename)
    clean_name = re.sub(r"[^\w\.\- ]", "_", clean_name)
    return clean_name


def validate_file_path(target_path: Path, allowed_directory: Path) -> bool:
    """Verify that the resolved target path stays strictly inside allowed directory."""
    try:
        resolved_target = target_path.resolve()
        resolved_dir = allowed_directory.resolve()
        return resolved_dir in resolved_target.parents or resolved_target == resolved_dir
    except (ValueError, RuntimeError):
        return False
