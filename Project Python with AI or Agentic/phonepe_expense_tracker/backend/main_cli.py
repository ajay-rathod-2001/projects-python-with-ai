"""
CLI Application Runner for PhonePe Expense Tracker
"""

import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding for emojis and currency symbols
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.src.services.tracker import ExpenseTrackerServices
from backend.src.utils.logger import setup_logger


def run_cli() -> None:
    logger = setup_logger()
    logger.info("Initializing PhonePe Expense Tracker CLI...")

    service = ExpenseTrackerServices()
    report = service.generate_report()
    summary = report.summary

    print("\n" + "=" * 55)
    print(" 📊 PHONEPE EXPENSE STUDIO - ENTERPRISE REPORT 📊 ")
    print("=" * 55 + "\n")
    print(f"Total Money Spent : ₹{summary.total_spent:.2f}")
    print(f"Monthly Budget    : ₹{summary.budget_limit:.2f} ({summary.utilization_percentage:.1f}% used)")
    print(f"Annual Budget     : ₹{summary.yearly_budget_limit:.2f} ({summary.yearly_utilization_percentage:.1f}% used)")

    print("\nSpending Breakdown by Category:")
    for category, amount in summary.category_totals.items():
        share = (amount / summary.total_spent) * 100 if summary.total_spent > 0 else 0
        print(f"    {category:14s}: ₹{amount:9.2f}  ({share:4.1f}%)")

    print("\nMonthly Breakdown:")
    for month_key, amount in summary.monthly_breakdown.items():
        print(f"    {month_key:14s}: ₹{amount:9.2f}")

    if summary.forecast:
        print("\nPredictive Forecast (Based on Active Daily Burn Rate):")
        print(f"    Daily Run-rate: ₹{summary.forecast.daily_average:.2f}/day")
        print(f"    3 Months Later: ₹{summary.forecast.projected_3_months:.2f}")
        print(f"    6 Months Later: ₹{summary.forecast.projected_6_months:.2f}")
        print(f"    1 Year Later  : ₹{summary.forecast.projected_1_year:.2f}")
        print(f"    5 Years Later : ₹{summary.forecast.projected_5_years:.2f}")

    print("-" * 55)

    if summary.is_over_budget:
        print(
            f"\n⚠️....WARNING: You have exceeded your monthly budget limit of ₹{summary.budget_limit:.2f}!....⚠️"
        )
        print(f"Monthly Overspend: +₹{summary.over_budget_amount:.2f}")
    else:
        print(
            f"\n🎉 Congratulations! You are within your monthly budget of ₹{summary.budget_limit:.2f}"
        )

    print("=" * 55 + "\n")


if __name__ == "__main__":
    run_cli()
