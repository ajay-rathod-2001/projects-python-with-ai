"""
File I/O handlers with proper exception handling and encoding
"""

import json
import logging
from pathlib import Path
from typing import List, Union

logger = logging.getLogger("PhonePeTracker")


def read_text_file(file_path: Union[str, Path]) -> List[str]:
    """Read a text file and return list of lines."""
    p = Path(file_path)
    if not p.exists():
        logger.error("File does not exist: %s", p)
        return []
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()
    except Exception as e:
        logger.error("Failed to read text file %s: %s", p, e)
        return []


def write_json_file(data: dict, output_path: Union[str, Path]) -> bool:
    """Write dictionary data to a formatted JSON file."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info("Summary JSON saved to %s", p)
        return True
    except Exception as e:
        logger.error("Failed to write JSON file %s: %s", p, e)
        return False

