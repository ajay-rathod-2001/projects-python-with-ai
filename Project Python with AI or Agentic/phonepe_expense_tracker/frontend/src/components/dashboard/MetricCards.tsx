import React from "react";
import { Wallet, ArrowUpRight, ShoppingBag, ShieldCheck, AlertCircle } from "lucide-react";
import { formatINR } from "../../lib/formatters";
import { Transaction } from "../../types/expense";

interface MetricCardsProps {
  totalSpent: number;
  highestExpense?: Transaction;
  topCategory: string;
  topCategoryAmount: number;
  validCount: number;
  skippedCount: number;
  onOpenSkippedModal: () => void;
}

export const MetricCards: React.FC<MetricCardsProps> = ({
  totalSpent,
  highestExpense,
  topCategory,
  topCategoryAmount,
  validCount,
  skippedCount,
  onOpenSkippedModal,
}) => {
  const topCategoryShare =
    totalSpent > 0 ? ((topCategoryAmount / totalSpent) * 100).toFixed(1) : "0.0";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
      {/* 1. Total Money Spent */}
      <div className="glass-card rounded-xl p-4 border border-phonepe-border hover:border-phonepe-accent/30 transition-all group">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Total Money Spent
          </span>
          <div className="w-8 h-8 rounded-lg bg-phonepe-purple/20 border border-phonepe-purple/30 flex items-center justify-center text-phonepe-light group-hover:scale-105 transition-transform">
            <Wallet className="w-4 h-4" />
          </div>
        </div>
        <div className="text-2xl font-bold text-white tracking-tight">
          {formatINR(totalSpent)}
        </div>
        <div className="mt-1.5 flex items-center text-[11px] text-slate-400">
          <span className="text-phonepe-light font-medium">Aggregated across all verified txns</span>
        </div>
      </div>

      {/* 2. Highest Single Expense */}
      <div className="glass-card rounded-xl p-4 border border-phonepe-border hover:border-amber-500/30 transition-all group">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Highest Expense
          </span>
          <div className="w-8 h-8 rounded-lg bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 group-hover:scale-105 transition-transform">
            <ArrowUpRight className="w-4 h-4" />
          </div>
        </div>
        <div className="text-2xl font-bold text-white tracking-tight">
          {highestExpense ? formatINR(highestExpense.amount) : "₹0.00"}
        </div>
        <div className="mt-1.5 text-[11px] text-slate-400 truncate">
          {highestExpense ? (
            <span title={highestExpense.merchant}>
              <strong className="text-slate-200">{highestExpense.merchant}</strong> ({highestExpense.category})
            </span>
          ) : (
            "No transactions"
          )}
        </div>
      </div>

      {/* 3. Top Spending Category */}
      <div className="glass-card rounded-xl p-4 border border-phonepe-border hover:border-pink-500/30 transition-all group">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Top Category
          </span>
          <div className="w-8 h-8 rounded-lg bg-pink-500/20 border border-pink-500/30 flex items-center justify-center text-pink-400 group-hover:scale-105 transition-transform">
            <ShoppingBag className="w-4 h-4" />
          </div>
        </div>
        <div className="text-2xl font-bold text-white tracking-tight">
          {topCategory}
        </div>
        <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-400">
          <span>{formatINR(topCategoryAmount)}</span>
          <span className="text-pink-400 font-semibold">{topCategoryShare}% of total</span>
        </div>
      </div>

      {/* 4. Data Health & Line Diagnostics */}
      <div className="glass-card rounded-xl p-4 border border-phonepe-border hover:border-blue-500/30 transition-all group">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Data Integrity
          </span>
          <div className="w-8 h-8 rounded-lg bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 group-hover:scale-105 transition-transform">
            <ShieldCheck className="w-4 h-4" />
          </div>
        </div>
        <div className="text-2xl font-bold text-white tracking-tight flex items-baseline gap-2">
          <span>{validCount}</span>
          <span className="text-xs font-normal text-slate-400">Valid Transactions</span>
        </div>
        <div className="mt-1.5 flex items-center justify-between text-[11px]">
          {skippedCount > 0 ? (
            <button
              onClick={onOpenSkippedModal}
              className="flex items-center gap-1 text-amber-400 hover:text-amber-300 font-medium transition-colors"
            >
              <AlertCircle className="w-3.5 h-3.5" />
              <span>{skippedCount} flagged line (Inspect)</span>
            </button>
          ) : (
            <span className="text-emerald-400">100% clean formatting</span>
          )}
        </div>
      </div>
    </div>
  );
};

