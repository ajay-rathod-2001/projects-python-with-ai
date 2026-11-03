import { useState, useEffect, useCallback } from "react";
import { AnalysisReport } from "../types/expense";

// High-fidelity fallback for standalone browser development
const MOCK_REPORT: AnalysisReport = {
  status: "success",
  meta: {
    filename: "transactions.txt",
    total_lines: 25,
    valid_count: 24,
    skipped_count: 1,
    processed_at: new Date().toISOString(),
  },
  summary: {
    total_spent: 15346.0,
    budget_limit: 10000.0,
    yearly_budget_limit: 120000.0,
    is_over_budget: true,
    over_budget_amount: 5346.0,
    utilization_percentage: 153.46,
    is_over_yearly_budget: false,
    yearly_over_budget_amount: 0.0,
    yearly_utilization_percentage: 12.79,
    category_totals: {
      Shopping: 5498.0,
      Bills: 3608.0,
      Food: 2480.0,
      Travel: 2320.0,
      Health: 1440.0,
    },
    top_category: "Shopping",
    top_category_amount: 5498.0,
    monthly_breakdown: {
      "2026-08": 15346.0,
    },
    yearly_breakdown: {
      "2026": 15346.0,
    },
    forecast: {
      daily_average: 613.84,
      projected_3_months: 55245.6,
      projected_6_months: 110491.2,
      projected_1_year: 224051.6,
      projected_2_years: 448103.2,
      projected_5_years: 1120258.0,
    },
    highest_expense: {
      id: "txn_13_20260813",
      date: "2026-08-13",
      merchant: "Electricity Bill Bescom",
      amount: 1850.0,
      category: "Bills",
      status: "Verified",
    },
  },
  transactions: [
    { id: "txn_1", date: "2026-08-01", merchant: "Swiggy", amount: 350, category: "Food", status: "Verified" },
    { id: "txn_2", date: "2026-08-02", merchant: "Uber Ride", amount: 180, category: "Travel", status: "Verified" },
    { id: "txn_3", date: "2026-08-03", merchant: "DMart Supermarket", amount: 1450, category: "Shopping", status: "Verified" },
    { id: "txn_4", date: "2026-08-04", merchant: "Zomato Food", amount: 220, category: "Food", status: "Verified" },
    { id: "txn_5", date: "2026-08-05", merchant: "Petrol Pump HPCL", amount: 600, category: "Travel", status: "Verified" },
    { id: "txn_6", date: "2026-08-06", merchant: "Amazon Purchase", amount: 999, category: "Shopping", status: "Verified" },
    { id: "txn_7", date: "2026-08-07", merchant: "Canteen Snacks", amount: 60, category: "Food", status: "Verified" },
    { id: "txn_8", date: "2026-08-08", merchant: "Mobile Recharge Jio", amount: 299, category: "Bills", status: "Verified" },
    { id: "txn_10", date: "2026-08-10", merchant: "Tea Stall", amount: 40, category: "Food", status: "Verified" },
    { id: "txn_11", date: "2026-08-11", merchant: "Flipkart Order", amount: 1299, category: "Shopping", status: "Verified" },
    { id: "txn_12", date: "2026-08-12", merchant: "Ola Mini Ride", amount: 215, category: "Travel", status: "Verified" },
    { id: "txn_13", date: "2026-08-13", merchant: "Electricity Bill Bescom", amount: 1850, category: "Bills", status: "Verified" },
    { id: "txn_14", date: "2026-08-14", merchant: "Restaurant Dinner", amount: 850, category: "Food", status: "Verified" },
    { id: "txn_15", date: "2026-08-15", merchant: "Broadband Wifi Bill Airtel", amount: 799, category: "Bills", status: "Verified" },
    { id: "txn_16", date: "2026-08-16", merchant: "Metro Card Recharge", amount: 500, category: "Travel", status: "Verified" },
    { id: "txn_17", date: "2026-08-17", merchant: "Myntra Fashion Shopping", amount: 1750, category: "Shopping", status: "Verified" },
    { id: "txn_18", date: "2026-08-18", merchant: "Rapido Bike Taxi", amount: 75, category: "Travel", status: "Verified" },
    { id: "txn_19", date: "2026-08-19", merchant: "Swiggy Instamart", amount: 420, category: "Food", status: "Verified" },
    { id: "txn_20", date: "2026-08-20", merchant: "Cinema Movie Ticket", amount: 350, category: "Entertainment", status: "Verified" },
    { id: "txn_21", date: "2026-08-21", merchant: "Petrol Pump BPCL", amount: 750, category: "Travel", status: "Verified" },
    { id: "txn_22", date: "2026-08-22", merchant: "Pharmacy Medical Store", amount: 240, category: "Health", status: "Verified" },
    { id: "txn_23", date: "2026-08-23", merchant: "Zomato Delivery", amount: 540, category: "Food", status: "Verified" },
    { id: "txn_24", date: "2026-08-24", merchant: "Water Bill Payment", amount: 310, category: "Bills", status: "Verified" },
    { id: "txn_25", date: "2026-08-25", merchant: "Gym Membership", amount: 1200, category: "Health", status: "Verified" },
  ],
  skipped_lines: [
    {
      line_number: 9,
      raw_content: "2026-08-09, Invalid Line Without Comma",
      reason: "Expected 3 comma-separated fields (date, merchant, amount), got 2",
    },
  ],
};

export function useDesktopApi() {
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isPyWebView, setIsPyWebView] = useState<boolean>(false);

  const fetchInitialData = useCallback(async () => {
    setLoading(true);
    try {
      if (window.pywebview && window.pywebview.api) {
        setIsPyWebView(true);
        const data = await window.pywebview.api.get_initial_data();
        setReport(data);
      } else {
        // Fallback for standalone browser dev
        setIsPyWebView(false);
        setReport(MOCK_REPORT);
      }
    } catch (err) {
      console.error("Failed to load initial data from pywebview:", err);
      setReport(MOCK_REPORT);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // pywebview attaches api asynchronously when DOM is ready
    if (window.pywebview) {
      fetchInitialData();
    } else {
      window.addEventListener("pywebviewready", fetchInitialData);
      const timer = setTimeout(() => {
        if (!window.pywebview) {
          fetchInitialData();
        }
      }, 300);
      return () => {
        window.removeEventListener("pywebviewready", fetchInitialData);
        clearTimeout(timer);
      };
    }
  }, [fetchInitialData]);

  const openNativeFileDialog = async () => {
    if (window.pywebview && window.pywebview.api) {
      setLoading(true);
      try {
        const res = await window.pywebview.api.open_file_dialog();
        if (res && res.status === "success") {
          setReport(res);
        } else if (res && res.status === "error") {
          alert(`Error reading file: ${res.message || "Unknown error"}`);
        }
      } catch (err) {
        console.error("Error in open_file_dialog:", err);
      } finally {
        setLoading(false);
      }
    }
  };

  const uploadRawText = async (content: string, filename: string) => {
    setLoading(true);
    try {
      if (window.pywebview && window.pywebview.api) {
        const res = await window.pywebview.api.analyze_raw_text(content, filename);
        if (res.status === "success") {
          setReport(res);
        } else {
          alert(`Analysis Error: ${res.message || "Failed to process content"}`);
        }
      } else {
        // Local preview in browser mode
        setReport((prev) => {
          if (!prev) return MOCK_REPORT;
          return {
            ...prev,
            meta: {
              ...prev.meta,
              filename,
            },
          };
        });
      }
    } catch (err) {
      console.error("Error analyzing raw text:", err);
      alert("Failed to analyze transactions file. Please verify formatting.");
    } finally {
      setLoading(false);
    }
  };

  const updateBudget = async (monthlyLimit: number, yearlyLimit?: number) => {
    const finalYearly = yearlyLimit && yearlyLimit > 0 ? yearlyLimit : monthlyLimit * 12;

    if (window.pywebview && window.pywebview.api) {
      setLoading(true);
      try {
        const res = await window.pywebview.api.update_budget_limit(monthlyLimit, finalYearly);
        if (res.status === "success") {
          setReport(res);
        }
      } catch (err) {
        console.error("Error updating budget:", err);
      } finally {
        setLoading(false);
      }
    } else if (report) {
      // Mock update in browser
      const spent = report.summary.total_spent;
      const isOver = spent > monthlyLimit;
      const isOverYearly = spent > finalYearly;
      setReport({
        ...report,
        summary: {
          ...report.summary,
          budget_limit: monthlyLimit,
          yearly_budget_limit: finalYearly,
          is_over_budget: isOver,
          over_budget_amount: Math.max(0, spent - monthlyLimit),
          utilization_percentage: Number(((spent / monthlyLimit) * 100).toFixed(2)),
          is_over_yearly_budget: isOverYearly,
          yearly_over_budget_amount: Math.max(0, spent - finalYearly),
          yearly_utilization_percentage: Number(((spent / finalYearly) * 100).toFixed(2)),
        },
      });
    }
  };

  const windowControls = {
    minimize: () => window.pywebview?.api?.minimize_window?.(),
    maximize: () => window.pywebview?.api?.maximize_window?.(),
    close: () => window.pywebview?.api?.close_window?.(),
  };

  return {
    report,
    loading,
    isPyWebView,
    openNativeFileDialog,
    uploadRawText,
    updateBudget,
    windowControls,
  };
}
