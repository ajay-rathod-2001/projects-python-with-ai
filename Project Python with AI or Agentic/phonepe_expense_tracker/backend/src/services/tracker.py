"""
Expense Tracker Analytics Service with Multi-Format Support (.txt, .csv, .xlsx)
"""

import csv
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Union, Dict, Set

from backend.src.config.setting import (
    BUDGET_LIMIT,
    YEARLY_BUDGET_LIMIT,
    DATA_FILE_PATH,
    OUTPUT_JSON_PATH,
)
from backend.src.models.expense import (
    AnalysisReport,
    ExpenseSummary,
    ExpenseForecast,
    SkippedLine,
    Transaction,
)
from backend.src.services.categorizer import CategorizerService
from backend.src.utils.decoratots import timer
from backend.src.utils.file_handler import read_text_file, write_json_file

logger = logging.getLogger("PhonePeTracker")


def read_excel_lines(file_path: Path) -> List[str]:
    """Extract rows from Excel worksheet as CSV-formatted lines."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        lines = []
        for row in sheet.iter_rows(values_only=True):
            if not row or not any(row):
                continue
            cells = []
            for cell in row:
                if cell is None:
                    cells.append("")
                elif isinstance(cell, datetime):
                    cells.append(cell.strftime("%Y-%m-%d"))
                else:
                    cells.append(str(cell).strip())
            if any(cells):
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(cells)
                lines.append(output.getvalue().strip())
        return lines
    except Exception as e:
        logger.error("Failed to read Excel file %s: %s", file_path, e)
        return []


def normalize_date(raw_date: str) -> str:
    """Normalize various date formats to ISO YYYY-MM-DD."""
    if not raw_date:
        return ""
    raw = raw_date.strip()

    # If it's a timestamp like '2026-08-01 14:30:00', take the date part
    tokens = raw.split()
    if len(tokens) == 2 and (":" in tokens[1] or tokens[1].lower() in ("am", "pm")):
        raw = tokens[0]

    # Try standard string formats first
    for fmt in (
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%b %d %Y",
        "%B %d %Y",
        "%d-%b-%Y",
        "%d-%B-%Y",
        "%Y.%m.%d",
        "%d.%m.%Y",
    ):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Fallback to manual dash normalization
    cleaned = raw.replace("/", "-").strip()
    parts = cleaned.split("-")
    if len(parts) == 3:
        if len(parts[0]) <= 2 and len(parts[2]) == 4:
            return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        if len(parts[0]) == 4:
            return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"

    return cleaned


class ExpenseTrackerServices:
    def __init__(
        self,
        data_path: Union[str, Path] = DATA_FILE_PATH,
        budget_limit: float = BUDGET_LIMIT,
        yearly_budget_limit: float = YEARLY_BUDGET_LIMIT,
        categorizer: CategorizerService = None,
    ):
        self.data_path = Path(data_path)
        self.budget_limit = float(budget_limit)
        self.yearly_budget_limit = float(yearly_budget_limit)
        self.categorizer = categorizer or CategorizerService()

    @timer
    def parse_lines(self, lines: List[str]) -> Tuple[List[Transaction], List[SkippedLine]]:
        """Parse raw text, CSV, or TSV lines into valid transactions and flagged errors.
        
        Supports 3-column, 4-column (with category), and 5-column (with status) files,
        as well as dynamic header detection.
        """
        transactions: List[Transaction] = []
        skipped_lines: List[SkippedLine] = []

        # Use CSV reader for resilient delimiter and quote handling
        clean_lines = [l.strip() for l in lines if l.strip()]
        csv_reader = csv.reader(clean_lines)

        header_map: Optional[Dict[str, int]] = None

        for line_idx, parts in enumerate(csv_reader, start=1):
            if not parts or not any(parts):
                continue

            # Strip whitespace
            parts = [p.strip() for p in parts if p is not None]

            # Detect and ignore header rows
            lower_parts = [p.lower() for p in parts]
            has_header_keywords = any(
                any(kw in p for kw in ("date", "merchant", "amount", "category", "debit", "spent", "status"))
                for p in lower_parts
            )

            # Check if this row could be actual data (contains a valid float amount)
            could_be_data = False
            for p in parts:
                clean_p = (
                    p.replace("₹", "")
                    .replace("$", "")
                    .replace("INR", "")
                    .replace(",", "")
                    .strip()
                )
                try:
                    float(clean_p)
                    could_be_data = True
                    break
                except ValueError:
                    pass

            if has_header_keywords and not could_be_data:
                header_map = {}
                for idx, col in enumerate(lower_parts):
                    if "date" in col or "time" in col:
                        header_map["date"] = idx
                    elif any(m in col for m in ("merchant", "desc", "details", "paid", "name", "party")):
                        header_map["merchant"] = idx
                    elif any(a in col for a in ("amount", "debit", "spent", "inr", "price", "cost")):
                        header_map["amount"] = idx
                    elif "category" in col or "type" in col:
                        header_map["category"] = idx
                logger.info("Header row detected and mapped at line %d: %s", line_idx, header_map)
                continue

            if len(parts) < 3:
                reason = f"Expected 3 comma-separated fields (date, merchant, amount), got {len(parts)}"
                raw_repr = ", ".join(parts)
                skipped_lines.append(SkippedLine(line_idx, raw_repr, reason))
                logger.warning("Line %d skipped: %s", line_idx, reason)
                continue

            date_str: Optional[str] = None
            merchant: Optional[str] = None
            amount: Optional[float] = None
            explicit_category: Optional[str] = None

            # Path A: Extract using header mapping if available
            if header_map and "amount" in header_map and "date" in header_map:
                try:
                    d_idx = header_map["date"]
                    m_idx = header_map.get("merchant", 1 if d_idx != 1 else 0)
                    a_idx = header_map["amount"]
                    c_idx = header_map.get("category")

                    if d_idx < len(parts):
                        date_str = parts[d_idx]
                    if m_idx < len(parts):
                        merchant = parts[m_idx]
                    if a_idx < len(parts):
                        clean_a = (
                            parts[a_idx]
                            .replace("₹", "")
                            .replace("$", "")
                            .replace("INR", "")
                            .replace(",", "")
                            .strip()
                        )
                        amount = float(clean_a)
                    if c_idx is not None and c_idx < len(parts) and parts[c_idx]:
                        explicit_category = parts[c_idx]
                except Exception:
                    amount = None

            # Path B: Resilient heuristic column inference (works for 3, 4, 5+ columns)
            if amount is None or date_str is None or merchant is None:
                date_str = parts[0]

                # Identify the amount column by scanning right-to-left
                amount_idx = None
                for idx in range(len(parts) - 1, 0, -1):
                    val = (
                        parts[idx]
                        .replace("₹", "")
                        .replace("$", "")
                        .replace("INR", "")
                        .replace(",", "")
                        .strip()
                    )
                    try:
                        parsed_val = float(val)
                        if parsed_val >= 0:
                            amount = parsed_val
                            amount_idx = idx
                            break
                    except ValueError:
                        continue

                if amount is None:
                    reason = f"Invalid amount format in row: '{parts[2] if len(parts) > 2 else ', '.join(parts)}'"
                    skipped_lines.append(SkippedLine(line_idx, ", ".join(parts), reason))
                    logger.warning("Line %d skipped: %s", line_idx, reason)
                    continue

                merchant_idx = 1 if amount_idx != 1 else 2
                merchant = parts[merchant_idx] if merchant_idx < len(parts) else "Unknown"

                # Check if there is an explicit category column
                for idx in range(1, len(parts)):
                    if idx != amount_idx and idx != merchant_idx and parts[idx]:
                        explicit_category = parts[idx]
                        break

            # Validate cleaned date
            date_clean = normalize_date(date_str)
            if not date_clean:
                reason = f"Invalid date format '{date_str}'"
                skipped_lines.append(SkippedLine(line_idx, ", ".join(parts), reason))
                continue

            if amount < 0:
                reason = "Amount cannot be negative"
                skipped_lines.append(SkippedLine(line_idx, ", ".join(parts), reason))
                continue

            category = explicit_category or self.categorizer.get_category(merchant)
            txn_id = f"txn_{line_idx}_{date_clean.replace('-', '')}"

            transactions.append(
                Transaction(
                    id=txn_id,
                    date=date_clean,
                    merchant=merchant,
                    amount=round(amount, 2),
                    category=category,
                    status="Verified",
                )
            )

        return transactions, skipped_lines

    @timer
    def parse_transaction(self) -> Tuple[List[Transaction], List[SkippedLine]]:
        """Read from configured file path (supports .txt, .csv, and .xlsx)."""
        suffix = self.data_path.suffix.lower()
        if suffix in [".xlsx", ".xls"]:
            raw_lines = read_excel_lines(self.data_path)
        else:
            raw_lines = read_text_file(self.data_path)
        return self.parse_lines(raw_lines)

    @timer
    def generate_report(
        self, custom_lines: List[str] = None, source_name: str = None
    ) -> AnalysisReport:
        """Generate comprehensive analytics report with metrics, charts data, and diagnostics."""
        if custom_lines is not None:
            transactions, skipped = self.parse_lines(custom_lines)
            filename = source_name or "uploaded_content.txt"
        else:
            transactions, skipped = self.parse_transaction()
            filename = self.data_path.name

        totals: dict[str, float] = {}
        monthly_breakdown: dict[str, float] = {}
        yearly_breakdown: dict[str, float] = {}
        unique_dates: Set[str] = set()
        total_spent = 0.0
        highest_txn: Transaction = None

        for txn in transactions:
            totals[txn.category] = totals.get(txn.category, 0.0) + txn.amount
            total_spent += txn.amount
            unique_dates.add(txn.date)

            # Month key (YYYY-MM) and Year key (YYYY)
            date_parts = txn.date.split("-")
            if len(date_parts) >= 2:
                month_key = f"{date_parts[0]}-{date_parts[1]}"
                monthly_breakdown[month_key] = monthly_breakdown.get(month_key, 0.0) + txn.amount
                year_key = date_parts[0]
                yearly_breakdown[year_key] = yearly_breakdown.get(year_key, 0.0) + txn.amount

            if highest_txn is None or txn.amount > highest_txn.amount:
                highest_txn = txn

        # Sort category totals descending by amount
        sorted_categories = dict(
            sorted(
                {k: round(v, 2) for k, v in totals.items()}.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

        sorted_monthly = {k: round(v, 2) for k, v in sorted(monthly_breakdown.items())}
        sorted_yearly = {k: round(v, 2) for k, v in sorted(yearly_breakdown.items())}

        top_cat = next(iter(sorted_categories.keys())) if sorted_categories else "None"
        top_cat_amount = sorted_categories.get(top_cat, 0.0)

        total_spent = round(total_spent, 2)

        # Monthly budget calculations
        is_over = total_spent > self.budget_limit
        over_amount = round(max(0.0, total_spent - self.budget_limit), 2)
        utilization = (
            round((total_spent / self.budget_limit) * 100, 2)
            if self.budget_limit > 0
            else 0.0
        )

        # Yearly budget calculations
        is_over_yearly = total_spent > self.yearly_budget_limit
        over_yearly_amount = round(max(0.0, total_spent - self.yearly_budget_limit), 2)
        yearly_utilization = (
            round((total_spent / self.yearly_budget_limit) * 100, 2)
            if self.yearly_budget_limit > 0
            else 0.0
        )

        # Forecasting engine based on active spending days
        days_count = max(1, len(unique_dates))
        daily_avg = round(total_spent / days_count, 2)
        forecast = ExpenseForecast(
            daily_average=daily_avg,
            projected_3_months=round(daily_avg * 90, 2),
            projected_6_months=round(daily_avg * 180, 2),
            projected_1_year=round(daily_avg * 365, 2),
            projected_2_years=round(daily_avg * 730, 2),
            projected_5_years=round(daily_avg * 1825, 2),
        )

        summary = ExpenseSummary(
            total_spent=total_spent,
            budget_limit=round(self.budget_limit, 2),
            yearly_budget_limit=round(self.yearly_budget_limit, 2),
            is_over_budget=is_over,
            over_budget_amount=over_amount,
            utilization_percentage=utilization,
            is_over_yearly_budget=is_over_yearly,
            yearly_over_budget_amount=over_yearly_amount,
            yearly_utilization_percentage=yearly_utilization,
            category_totals=sorted_categories,
            top_category=top_cat,
            top_category_amount=top_cat_amount,
            monthly_breakdown=sorted_monthly,
            yearly_breakdown=sorted_yearly,
            forecast=forecast,
            highest_expense=highest_txn,
        )

        total_lines_counted = len(transactions) + len(skipped)
        meta = {
            "filename": filename,
            "total_lines": total_lines_counted,
            "valid_count": len(transactions),
            "skipped_count": len(skipped),
            "processed_at": datetime.now().isoformat(),
        }

        report = AnalysisReport(
            status="success",
            meta=meta,
            summary=summary,
            transactions=transactions,
            skipped_lines=skipped,
        )

        # Cache summary to JSON
        self.save_summary(report.to_dict())
        return report

    def save_summary(self, report_dict: dict, output_path: Path = OUTPUT_JSON_PATH) -> bool:
        """Save report dictionary to data/summary.json."""
        return write_json_file(report_dict, output_path)
