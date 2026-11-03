"""
Data Models for PhonePe Expense Studio
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


@dataclass
class Transaction:
    id: str
    date: str
    merchant: str
    amount: float
    category: str = "Other"
    status: str = "Verified"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SkippedLine:
    line_number: int
    raw_content: str
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExpenseForecast:
    daily_average: float
    projected_3_months: float
    projected_6_months: float
    projected_1_year: float
    projected_2_years: float
    projected_5_years: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExpenseSummary:
    total_spent: float
    budget_limit: float                     # Monthly budget
    yearly_budget_limit: float              # Yearly budget
    is_over_budget: bool                    # Monthly check
    over_budget_amount: float
    utilization_percentage: float
    is_over_yearly_budget: bool             # Yearly check
    yearly_over_budget_amount: float
    yearly_utilization_percentage: float
    category_totals: Dict[str, float]
    top_category: str
    top_category_amount: float
    monthly_breakdown: Dict[str, float]     # e.g. {"2026-08": 15346.00}
    yearly_breakdown: Dict[str, float]      # e.g. {"2026": 15346.00}
    forecast: Optional[ExpenseForecast] = None
    highest_expense: Optional[Transaction] = None

    def to_dict(self) -> dict:
        data = asdict(self)
        if self.highest_expense:
            data["highest_expense"] = self.highest_expense.to_dict()
        if self.forecast:
            data["forecast"] = self.forecast.to_dict()
        return data


@dataclass
class AnalysisReport:
    status: str
    meta: Dict[str, Any]
    summary: ExpenseSummary
    transactions: List[Transaction] = field(default_factory=list)
    skipped_lines: List[SkippedLine] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "meta": self.meta,
            "summary": self.summary.to_dict(),
            "transactions": [t.to_dict() for t in self.transactions],
            "skipped_lines": [s.to_dict() for s in self.skipped_lines],
        }
