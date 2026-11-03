"""
Unit Tests for PhonePe Expense Studio Backend Engine
"""

import unittest
from backend.src.services.tracker import ExpenseTrackerServices
from backend.src.services.categorizer import CategorizerService


class TestExpenseTracker(unittest.TestCase):
    def setUp(self):
        self.categorizer = CategorizerService()
        self.service = ExpenseTrackerServices(
            budget_limit=10000.0,
            yearly_budget_limit=120000.0,
            categorizer=self.categorizer,
        )

    def test_parse_valid_lines(self):
        lines = [
            "2026-08-01, Swiggy, 350\n",
            "2026-08-02, Uber Ride, 180.50\n",
        ]
        txns, skipped = self.service.parse_lines(lines)
        self.assertEqual(len(txns), 2)
        self.assertEqual(len(skipped), 0)
        self.assertEqual(txns[0].category, "Food")
        self.assertEqual(txns[0].amount, 350.0)
        self.assertEqual(txns[1].category, "Travel")
        self.assertEqual(txns[1].amount, 180.50)

    def test_syntax_fault_tolerance(self):
        lines = [
            "2026-08-01, Swiggy, 350\n",
            "2026-08-09, Invalid Line Without Comma\n",
            "2026-08-10, Tea Stall, not_a_number\n",
            "2026-08-11, Flipkart Order, 1299\n",
        ]
        txns, skipped = self.service.parse_lines(lines)
        self.assertEqual(len(txns), 2)
        self.assertEqual(len(skipped), 2)
        self.assertEqual(skipped[0].line_number, 2)
        self.assertIn("Expected 3", skipped[0].reason)
        self.assertEqual(skipped[1].line_number, 3)
        self.assertIn("Invalid amount", skipped[1].reason)

    def test_budget_overspend_calculation(self):
        lines = [
            "2026-08-01, DMart Supermarket, 6000\n",
            "2026-08-02, Amazon Purchase, 5500\n",
        ]
        report = self.service.generate_report(custom_lines=lines, source_name="test.txt")
        summary = report.summary
        self.assertEqual(summary.total_spent, 11500.0)
        self.assertTrue(summary.is_over_budget)
        self.assertEqual(summary.over_budget_amount, 1500.0)
        self.assertEqual(summary.utilization_percentage, 115.0)
        self.assertEqual(summary.top_category, "Shopping")
        self.assertEqual(summary.highest_expense.amount, 6000.0)

    def test_monthly_yearly_forecast(self):
        lines = [
            "2026-08-01, Swiggy, 500\n",
            "2026-08-02, Uber Ride, 500\n",
        ]
        report = self.service.generate_report(custom_lines=lines, source_name="test.txt")
        summary = report.summary
        self.assertEqual(summary.monthly_breakdown.get("2026-08"), 1000.0)
        self.assertEqual(summary.yearly_breakdown.get("2026"), 1000.0)
        self.assertIsNotNone(summary.forecast)
        self.assertEqual(summary.forecast.daily_average, 500.0)
        self.assertEqual(summary.forecast.projected_3_months, 45000.0)
        self.assertEqual(summary.forecast.projected_1_year, 182500.0)

    def test_dynamic_keyword_learning(self):
        categorizer = CategorizerService()
        self.assertEqual(categorizer.get_category("RandomStore"), "Other")
        success = categorizer.register_keyword("Shopping", "randomstore")
        self.assertTrue(success)
        self.assertEqual(categorizer.get_category("RandomStore"), "Shopping")

    def test_multi_column_and_header_resilience(self):
        # Tests 5-column format with header (matching export) and custom dates
        lines = [
            "Date,Merchant,Category,Amount,Status\n",
            "2026-08-01,Swiggy,Food,350,Verified\n",
            "02/08/2026,Uber Ride,Travel,180.50,Verified\n",
            "13 Aug 2026,Bescom Electricity,Bills,1850.00,Verified\n",
        ]
        txns, skipped = self.service.parse_lines(lines)
        self.assertEqual(len(txns), 3)
        self.assertEqual(len(skipped), 0)
        self.assertEqual(txns[0].amount, 350.0)
        self.assertEqual(txns[0].category, "Food")
        self.assertEqual(txns[1].date, "2026-08-02")
        self.assertEqual(txns[1].amount, 180.50)
        self.assertEqual(txns[2].date, "2026-08-13")
        self.assertEqual(txns[2].amount, 1850.0)


if __name__ == "__main__":
    unittest.main()
