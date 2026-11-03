"""
Desktop API Bridge between Python and React WebView
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional
import webview

from backend.src.config.setting import BUDGET_LIMIT, YEARLY_BUDGET_LIMIT, DATA_FILE_PATH
from backend.src.services.categorizer import CategorizerService
from backend.src.services.tracker import ExpenseTrackerServices

logger = logging.getLogger("PhonePeTracker")


class DesktopApi:
    """Exposed to window.pywebview.api in JavaScript.

    All internal state attributes MUST start with a leading underscore '_'
    so that PyWebView does not recursively inspect .NET WinForms / CLR objects
    and cause a 'maximum recursion depth exceeded' stack overflow error.
    """

    def __init__(self, window: Optional[webview.Window] = None):
        self._window: Optional[webview.Window] = window
        self._budget_limit: float = BUDGET_LIMIT
        self._yearly_budget_limit: float = YEARLY_BUDGET_LIMIT
        self._categorizer: CategorizerService = CategorizerService()
        self._service: ExpenseTrackerServices = ExpenseTrackerServices(
            data_path=DATA_FILE_PATH,
            budget_limit=self._budget_limit,
            yearly_budget_limit=self._yearly_budget_limit,
            categorizer=self._categorizer,
        )
        self._current_lines: Optional[list[str]] = None
        self._current_filename: str = DATA_FILE_PATH.name
        self._is_maximized: bool = False

    def set_window(self, window: webview.Window) -> None:
        self._window = window

    def get_initial_data(self) -> Dict[str, Any]:
        """Loads and returns initial analysis from default transactions.txt."""
        try:
            if DATA_FILE_PATH.exists():
                report = self._service.generate_report()
                with open(DATA_FILE_PATH, "r", encoding="utf-8", errors="replace") as f:
                    self._current_lines = f.readlines()
                self._current_filename = DATA_FILE_PATH.name
                return report.to_dict()
            else:
                return {
                    "status": "empty",
                    "meta": {"filename": "", "total_lines": 0, "valid_count": 0, "skipped_count": 0},
                    "summary": {
                        "total_spent": 0.0,
                        "budget_limit": self._budget_limit,
                        "yearly_budget_limit": self._yearly_budget_limit,
                        "is_over_budget": False,
                        "over_budget_amount": 0.0,
                        "utilization_percentage": 0.0,
                        "is_over_yearly_budget": False,
                        "yearly_over_budget_amount": 0.0,
                        "yearly_utilization_percentage": 0.0,
                        "category_totals": {},
                        "top_category": "None",
                        "top_category_amount": 0.0,
                        "monthly_breakdown": {},
                        "yearly_breakdown": {},
                        "forecast": {
                            "daily_average": 0.0,
                            "projected_3_months": 0.0,
                            "projected_6_months": 0.0,
                            "projected_1_year": 0.0,
                            "projected_2_years": 0.0,
                            "projected_5_years": 0.0,
                        },
                    },
                    "transactions": [],
                    "skipped_lines": [],
                }
        except Exception as e:
            logger.error("Failed to load initial data: %s", e)
            return {"status": "error", "message": str(e)}

    def analyze_file_path(self, file_path_str: str) -> Dict[str, Any]:
        """Analyze a file given its local filesystem path (supports .txt, .csv, .xlsx)."""
        try:
            path = Path(file_path_str.strip('"').strip("'"))
            if not path.exists():
                return {"status": "error", "message": f"File not found: {path}"}

            suffix = path.suffix.lower()
            if suffix in [".xlsx", ".xls"]:
                from backend.src.services.tracker import read_excel_lines
                lines = read_excel_lines(path)
            else:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()

            self._current_lines = lines
            self._current_filename = path.name

            report = self._service.generate_report(custom_lines=lines, source_name=path.name)
            return report.to_dict()
        except Exception as e:
            logger.error("Error analyzing file %s: %s", file_path_str, e)
            return {"status": "error", "message": str(e)}

    def analyze_raw_text(self, text_content: str, filename: str = "uploaded.txt") -> Dict[str, Any]:
        """Analyze text content passed directly from browser file reader."""
        try:
            lines = text_content.splitlines(keepends=True)
            self._current_lines = lines
            self._current_filename = filename

            report = self._service.generate_report(custom_lines=lines, source_name=filename)
            return report.to_dict()
        except Exception as e:
            logger.error("Error analyzing raw text: %s", e)
            return {"status": "error", "message": str(e)}

    def open_file_dialog(self) -> Optional[Dict[str, Any]]:
        """Open native OS file picker and parse selected file (.txt, .csv, .xlsx)."""
        if not self._window:
            return {"status": "error", "message": "Window context not attached"}

        file_types = (
            "All Supported Expense Files (*.txt;*.csv;*.xlsx;*.xls)",
            "Excel Spreadsheets (*.xlsx;*.xls)",
            "Text / CSV Data (*.txt;*.csv)",
            "All Files (*.*)",
        )
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types,
        )

        if result and len(result) > 0:
            selected_path = result[0]
            return self.analyze_file_path(selected_path)
        return {"status": "cancelled"}

    def update_budget_limit(self, monthly_limit: float, yearly_limit: Optional[float] = None) -> Dict[str, Any]:
        """Update monthly and/or yearly budget limit and recalculate analysis instantly."""
        try:
            self._budget_limit = float(monthly_limit)
            if yearly_limit is not None and float(yearly_limit) > 0:
                self._yearly_budget_limit = float(yearly_limit)
            else:
                # Default yearly to 12x monthly if not specified
                self._yearly_budget_limit = self._budget_limit * 12

            self._service.budget_limit = self._budget_limit
            self._service.yearly_budget_limit = self._yearly_budget_limit

            report = self._service.generate_report(
                custom_lines=self._current_lines, source_name=self._current_filename
            )
            return report.to_dict()
        except Exception as e:
            logger.error("Failed to update budget limits: %s", e)
            return {"status": "error", "message": str(e)}

    def add_category_keyword(self, category: str, keyword: str) -> Dict[str, Any]:
        """Register a new keyword rule and re-analyze the current dataset."""
        try:
            self._categorizer.register_keyword(category, keyword)
            report = self._service.generate_report(
                custom_lines=self._current_lines, source_name=self._current_filename
            )
            return report.to_dict()
        except Exception as e:
            logger.error("Failed to add category rule: %s", e)
            return {"status": "error", "message": str(e)}

    # Native Window Control Actions
    def minimize_window(self) -> None:
        if self._window:
            try:
                self._window.minimize()
            except Exception as e:
                logger.error("Failed to minimize window: %s", e)

    def maximize_window(self) -> None:
        if self._window:
            try:
                if self._is_maximized:
                    self._window.restore()
                    self._is_maximized = False
                else:
                    self._window.maximize()
                    self._is_maximized = True
            except Exception as e:
                logger.error("Failed to toggle maximize window: %s", e)

    def close_window(self) -> None:
        if self._window:
            try:
                self._window.destroy()
            except Exception as e:
                logger.error("Failed to close window: %s", e)
