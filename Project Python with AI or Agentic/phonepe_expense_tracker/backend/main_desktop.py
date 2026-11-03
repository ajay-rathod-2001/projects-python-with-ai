"""
Desktop Application Launcher for PhonePe Expense Studio
"""

import sys
from pathlib import Path
import webview

# Ensure backend and repository root are on python path
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.src.bridge.api import DesktopApi
from backend.src.config.setting import FRONTEND_DIST_PATH
from backend.src.utils.logger import setup_logger


def start_app(dev_url: str = None) -> None:
    setup_logger()

    # Explicitly configure PyWebView drag behavior:
    # Restrict drag to the dedicated '.pywebview-drag-region' title area only.
    # This prevents the whole window from capturing clicks on buttons, inputs, and tables.
    webview.settings["DRAG_REGION_SELECTOR"] = ".pywebview-drag-region"
    webview.settings["DRAG_REGION_DIRECT_TARGET_ONLY"] = True

    api = DesktopApi()

    # Determine frontend target
    if dev_url:
        target_url = dev_url
    elif (FRONTEND_DIST_PATH / "index.html").exists():
        target_url = str(FRONTEND_DIST_PATH / "index.html")
    else:
        target_url = "http://localhost:5173"

    window = webview.create_window(
        title="PhonePe Expense Studio",
        url=target_url,
        js_api=api,
        width=1240,
        height=840,
        min_size=(960, 640),
        frameless=True,
        easy_drag=False,  # MUST be False so mouse clicks reach HTML buttons, inputs & links
        text_select=True, # Enables text selection and input focus
        background_color="#090D16",
    )

    api.set_window(window)
    webview.start(debug=False)


if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else None
    start_app(dev_url=url_arg)
