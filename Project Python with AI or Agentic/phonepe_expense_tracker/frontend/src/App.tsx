import React, { useState, useEffect, useMemo } from "react";
import * as XLSX from "xlsx";
import { useDesktopApi } from "./hooks/useDesktopApi";
import { TitleBar } from "./components/layout/TitleBar";
import { DropZone } from "./components/upload/DropZone";
import { GlobalDropOverlay } from "./components/upload/GlobalDropOverlay";
import { BudgetBanner } from "./components/dashboard/BudgetBanner";
import { MetricCards } from "./components/dashboard/MetricCards";
import { CategoryDonut } from "./components/analytics/CategoryDonut";
import { SpendVelocity } from "./components/analytics/SpendVelocity";
import { FinancialRunwayAndMonths } from "./components/analytics/FinancialRunwayAndMonths";
import { TransactionTable } from "./components/ledger/TransactionTable";
import { SkippedLinesModal } from "./components/ledger/SkippedLinesModal";
import { EditBudgetModal } from "./components/dashboard/EditBudgetModal";
import { PhonePeLogo } from "./components/common/PhonePeLogo";
import { formatINR } from "./lib/formatters";
import { Loader2, Download, Calendar } from "lucide-react";

export const App: React.FC = () => {
  const {
    report,
    loading,
    isPyWebView,
    openNativeFileDialog,
    uploadRawText,
    updateBudget,
    windowControls,
  } = useDesktopApi();

  const [isSkippedModalOpen, setIsSkippedModalOpen] = useState(false);
  const [isBudgetModalOpen, setIsBudgetModalOpen] = useState(false);
  const [budgetViewMode, setBudgetViewMode] = useState<"monthly" | "yearly">("monthly");
  const [selectedMonth, setSelectedMonth] = useState<string>("all");
  const [isWindowDragging, setIsWindowDragging] = useState(false);

  // Global Drag & Drop listeners supporting .txt, .csv, and .xlsx
  useEffect(() => {
    let dragCounter = 0;

    const handleWindowDragEnter = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter++;
      if (e.dataTransfer && e.dataTransfer.types && Array.from(e.dataTransfer.types).includes("Files")) {
        setIsWindowDragging(true);
      }
    };

    const handleWindowDragOver = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
    };

    const handleWindowDragLeave = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter--;
      if (dragCounter === 0) {
        setIsWindowDragging(false);
      }
    };

    const handleWindowDrop = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter = 0;
      setIsWindowDragging(false);

      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        const ext = file.name.split(".").pop()?.toLowerCase();
        setSelectedMonth("all");

        if (ext === "xlsx" || ext === "xls") {
          const reader = new FileReader();
          reader.onload = (evt) => {
            try {
              const buffer = new Uint8Array(evt.target?.result as ArrayBuffer);
              const workbook = XLSX.read(buffer, { type: "array" });
              const sheetName = workbook.SheetNames[0];
              const worksheet = workbook.Sheets[sheetName];
              const csvText = XLSX.utils.sheet_to_csv(worksheet);
              uploadRawText(csvText, file.name);
            } catch (err) {
              console.error("Excel parse error:", err);
              alert("Failed to parse Excel spreadsheet.");
            }
          };
          reader.readAsArrayBuffer(file);
        } else {
          const reader = new FileReader();
          reader.onload = (evt) => {
            const content = evt.target?.result as string;
            if (content) {
              uploadRawText(content, file.name);
            }
          };
          reader.readAsText(file);
        }
      }
    };

    window.addEventListener("dragenter", handleWindowDragEnter);
    window.addEventListener("dragover", handleWindowDragOver);
    window.addEventListener("dragleave", handleWindowDragLeave);
    window.addEventListener("drop", handleWindowDrop);

    return () => {
      window.removeEventListener("dragenter", handleWindowDragEnter);
      window.removeEventListener("dragover", handleWindowDragOver);
      window.removeEventListener("dragleave", handleWindowDragLeave);
      window.removeEventListener("drop", handleWindowDrop);
    };
  }, [uploadRawText]);

  // Extract base report data
  const summary = report?.summary || {
    total_spent: 0,
    budget_limit: 10000,
    yearly_budget_limit: 120000,
    is_over_budget: false,
    over_budget_amount: 0,
    utilization_percentage: 0,
    is_over_yearly_budget: false,
    yearly_over_budget_amount: 0,
    yearly_utilization_percentage: 0,
    category_totals: {},
    top_category: "None",
    top_category_amount: 0,
    monthly_breakdown: {},
    yearly_breakdown: {},
  };

  const meta = report?.meta || {
    filename: "transactions.txt",
    total_lines: 0,
    valid_count: 0,
    skipped_count: 0,
  };

  const allTransactions = report?.transactions || [];
  const skippedLines = report?.skipped_lines || [];

  // Filter transactions when user selects a specific month (e.g. '2026-08')
  const activeTransactions = useMemo(() => {
    if (selectedMonth === "all") return allTransactions;
    return allTransactions.filter((tx) => tx.date.startsWith(selectedMonth));
  }, [allTransactions, selectedMonth]);

  // Recalculate category totals for the active month filter if filtered
  const activeCategoryTotals = useMemo(() => {
    if (selectedMonth === "all") return summary.category_totals;
    const totals: Record<string, number> = {};
    activeTransactions.forEach((tx) => {
      totals[tx.category] = (totals[tx.category] || 0) + tx.amount;
    });
    return totals;
  }, [activeTransactions, selectedMonth, summary.category_totals]);

  const activeTotalSpent = useMemo(() => {
    if (selectedMonth === "all") return summary.total_spent;
    return activeTransactions.reduce((acc, t) => acc + t.amount, 0);
  }, [activeTransactions, selectedMonth, summary.total_spent]);

  // CSV Export utility
  const exportToCSV = () => {
    if (allTransactions.length === 0) return;
    const headers = "Date,Merchant,Category,Amount,Status\n";
    const rows = allTransactions
      .map((t) => `"${t.date}","${t.merchant}","${t.category}",${t.amount},"${t.status}"`)
      .join("\n");
    const blob = new Blob([headers + rows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `phonepe_expenses_${meta.filename.replace(/\.[^/.]+$/, "")}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading && !report) {
    return (
      <div className="h-screen w-screen bg-phonepe-dark flex flex-col items-center justify-center text-slate-300">
        <div className="mb-4 animate-bounce">
          <PhonePeLogo size="lg" />
        </div>
        <div className="flex items-center gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-phonepe-accent" />
          <span className="text-xs font-bold tracking-wider uppercase text-slate-400">
            Initializing PhonePe Expense Studio...
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen flex flex-col bg-phonepe-dark text-slate-100 overflow-hidden font-sans select-none relative">
      {/* 1. Global Full-Screen Drag Overlay */}
      <GlobalDropOverlay isDragging={isWindowDragging} />

      {/* 2. Custom Frameless Title Bar */}
      <TitleBar
        onMinimize={windowControls.minimize}
        onMaximize={windowControls.maximize}
        onClose={windowControls.close}
        isDesktop={isPyWebView}
      />

      {/* 3. Main Scrollable Container */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-5 max-w-7xl mx-auto w-full">
        {/* Top Action Bar with Logo & Export */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-1 border-b border-white/5">
          <div className="flex items-center gap-3">
            <PhonePeLogo size="md" />
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-extrabold text-white tracking-tight">
                  PhonePe Expense Studio
                </h1>
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Enterprise Analytics
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Institutional Expense Analytics & Predictive Runway Suite
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {/* Filter Indicator */}
            {selectedMonth !== "all" && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/30 text-xs font-semibold">
                <Calendar className="w-3.5 h-3.5 text-phonepe-light" />
                <span>Filtered: {selectedMonth}</span>
                <button
                  type="button"
                  onClick={() => setSelectedMonth("all")}
                  className="ml-1 text-slate-400 hover:text-white"
                >
                  ✕
                </button>
              </span>
            )}

            <button
              type="button"
              onClick={exportToCSV}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-200 hover:text-white transition-all shadow-sm active:scale-95 cursor-pointer"
              title="Export Transactions to CSV"
            >
              <Download className="w-3.5 h-3.5 text-phonepe-accent" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>

        {/* Ingestion DropZone */}
        <DropZone
          onFileLoaded={(content, filename) => {
            setSelectedMonth("all");
            uploadRawText(content, filename);
          }}
          onNativeBrowse={async () => {
            setSelectedMonth("all");
            await openNativeFileDialog();
          }}
          currentFilename={meta.filename}
          isDesktop={isPyWebView}
          isLoading={loading}
        />

        {/* Dynamic Monthly / Yearly Budget Alert Banner */}
        <BudgetBanner
          totalSpent={activeTotalSpent}
          monthlyBudget={summary.budget_limit}
          yearlyBudget={summary.yearly_budget_limit}
          isOverMonthlyBudget={summary.is_over_budget}
          monthlyOverBudgetAmount={summary.over_budget_amount}
          monthlyUtilization={summary.utilization_percentage}
          isOverYearlyBudget={summary.is_over_yearly_budget}
          yearlyOverBudgetAmount={summary.yearly_over_budget_amount}
          yearlyUtilization={summary.yearly_utilization_percentage}
          viewMode={budgetViewMode}
          onToggleViewMode={setBudgetViewMode}
          onEditBudget={() => setIsBudgetModalOpen(true)}
          projectedOneYear={summary.forecast?.projected_1_year}
        />

        {/* 4 Hero Metric Cards */}
        <MetricCards
          totalSpent={activeTotalSpent}
          highestExpense={summary.highest_expense}
          topCategory={summary.top_category}
          topCategoryAmount={summary.top_category_amount}
          validCount={activeTransactions.length}
          skippedCount={meta.skipped_count}
          onOpenSkippedModal={() => setIsSkippedModalOpen(true)}
        />

        {/* Enterprise Multi-Month Breakdown with Choose Option & 3M, 6M, 1Y, 2Y, 5Y Forecasting */}
        <FinancialRunwayAndMonths
          monthlyBreakdown={summary.monthly_breakdown}
          yearlyBreakdown={summary.yearly_breakdown}
          forecast={summary.forecast}
          monthlyBudget={summary.budget_limit}
          yearlyBudget={summary.yearly_budget_limit}
          selectedMonth={selectedMonth}
          onSelectMonth={setSelectedMonth}
        />

        {/* Active Month Filter Notification Banner */}
        {selectedMonth !== "all" && (
          <div className="flex items-center justify-between p-3.5 px-4 rounded-xl bg-purple-950/70 border border-purple-500/40 text-xs text-purple-200 shadow-md animate-in fade-in">
            <div className="flex items-center gap-2.5">
              <span className="w-2.5 h-2.5 rounded-full bg-phonepe-accent animate-pulse" />
              <span>
                Filtered by period: <strong className="text-white font-mono">{selectedMonth}</strong> ({activeTransactions.length} transaction{activeTransactions.length === 1 ? "" : "s"} • {formatINR(activeTotalSpent)})
              </span>
            </div>
            <button
              type="button"
              onClick={() => setSelectedMonth("all")}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-phonepe-purple hover:bg-purple-600 text-white font-bold transition-all shadow-sm active:scale-95 cursor-pointer text-xs"
            >
              <span>Show All Months ({allTransactions.length})</span>
            </button>
          </div>
        )}

        {/* Conditional Content: Graceful Empty State Card OR Analytics Charts & Ledger */}
        {activeTransactions.length === 0 ? (
          <div className="glass-card rounded-2xl p-10 border border-white/10 text-center flex flex-col items-center justify-center space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-phonepe-light mb-1">
              <Calendar className="w-7 h-7" />
            </div>
            <h3 className="text-base font-bold text-white">
              No Transactions Recorded in {selectedMonth}
            </h3>
            <p className="text-xs text-slate-400 max-w-md">
              There are no expenses logged for this month. Pick another month from the breakdown chart above, or click below to view all transactions across all months.
            </p>
            <button
              type="button"
              onClick={() => setSelectedMonth("all")}
              className="mt-2 px-4 py-2 rounded-xl bg-phonepe-purple hover:bg-purple-600 text-xs font-bold text-white shadow-lg transition-transform active:scale-95 cursor-pointer"
            >
              Reset Filter to All Months ({allTransactions.length} Total)
            </button>
          </div>
        ) : (
          <>
            {/* Analytics Grid: Category Donut & Velocity Graph */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <CategoryDonut
                categoryTotals={activeCategoryTotals}
                totalSpent={activeTotalSpent}
              />
              <SpendVelocity transactions={activeTransactions} />
            </div>

            {/* Searchable Transaction Table */}
            <TransactionTable transactions={activeTransactions} />
          </>
        )}

        {/* Diagnostics & Modals */}
        <SkippedLinesModal
          isOpen={isSkippedModalOpen}
          onClose={() => setIsSkippedModalOpen(false)}
          skippedLines={skippedLines}
        />

        <EditBudgetModal
          isOpen={isBudgetModalOpen}
          onClose={() => setIsBudgetModalOpen(false)}
          currentMonthlyBudget={summary.budget_limit}
          currentYearlyBudget={summary.yearly_budget_limit}
          onSave={updateBudget}
        />
      </div>

      {/* 4. Status Bar */}
      <footer className="h-7 bg-phonepe-darker border-t border-phonepe-border/80 px-4 flex items-center justify-between text-[11px] text-slate-400 select-none flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Core: Python 3.14 Engine</span>
          <span>•</span>
          <span>Shell: Microsoft Edge WebView2</span>
          <span>•</span>
          <span>Monthly Target: ₹{summary.budget_limit}</span>
          <span>•</span>
          <span>Annual Target: ₹{summary.yearly_budget_limit}</span>
        </div>
        <div className="flex items-center gap-3">
          <span>Processed {meta.total_lines} lines ({meta.valid_count} verified)</span>
          <span>•</span>
          <span className="text-slate-300 font-medium">PhonePe Expense Studio v2.0 Enterprise</span>
        </div>
      </footer>
    </div>
  );
};
