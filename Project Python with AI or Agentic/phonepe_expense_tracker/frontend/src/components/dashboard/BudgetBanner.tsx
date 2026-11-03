import React from "react";
import { AlertTriangle, CheckCircle2, Sliders } from "lucide-react";
import { formatINR } from "../../lib/formatters";

interface BudgetBannerProps {
  totalSpent: number;
  monthlyBudget: number;
  yearlyBudget: number;
  isOverMonthlyBudget: boolean;
  monthlyOverBudgetAmount: number;
  monthlyUtilization: number;
  isOverYearlyBudget: boolean;
  yearlyOverBudgetAmount: number;
  yearlyUtilization: number;
  viewMode: "monthly" | "yearly";
  onToggleViewMode: (mode: "monthly" | "yearly") => void;
  onEditBudget: () => void;
  projectedOneYear?: number;
}

export const BudgetBanner: React.FC<BudgetBannerProps> = ({
  totalSpent,
  monthlyBudget,
  yearlyBudget,
  isOverMonthlyBudget,
  monthlyOverBudgetAmount,
  monthlyUtilization,
  isOverYearlyBudget,
  yearlyOverBudgetAmount,
  yearlyUtilization,
  viewMode,
  onToggleViewMode,
  onEditBudget,
  projectedOneYear,
}) => {
  const isMonthly = viewMode === "monthly";
  const activeLimit = isMonthly ? monthlyBudget : yearlyBudget;
  const isOver = isMonthly ? isOverMonthlyBudget : isOverYearlyBudget;
  const overAmount = isMonthly ? monthlyOverBudgetAmount : yearlyOverBudgetAmount;
  const utilization = isMonthly ? monthlyUtilization : yearlyUtilization;

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border p-5 transition-all duration-300 ${
        isOver
          ? "bg-gradient-to-r from-rose-950/45 via-red-950/20 to-slate-900/60 border-rose-500/35 shadow-xl shadow-rose-950/25"
          : "bg-gradient-to-r from-emerald-950/40 via-teal-950/20 to-slate-900/60 border-emerald-500/35 shadow-xl shadow-emerald-950/25"
      }`}
    >
      {/* Background ambient lighting */}
      <div
        className={`absolute -right-16 -top-16 w-56 h-56 rounded-full blur-3xl opacity-25 pointer-events-none ${
          isOver ? "bg-rose-500" : "bg-emerald-500"
        }`}
      />

      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 relative z-10">
        <div className="flex items-start gap-4">
          <div
            className={`p-3 rounded-2xl border flex-shrink-0 shadow-inner ${
              isOver
                ? "bg-rose-500/15 border-rose-500/30 text-rose-400 animate-pulse"
                : "bg-emerald-500/15 border-emerald-500/30 text-emerald-400"
            }`}
          >
            {isOver ? <AlertTriangle className="w-6 h-6" /> : <CheckCircle2 className="w-6 h-6" />}
          </div>

          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <h3
                className={`text-sm font-extrabold tracking-wide uppercase ${
                  isOver ? "text-rose-400" : "text-emerald-400"
                }`}
              >
                {isMonthly ? "Monthly Budget Status" : "Annual / Yearly Budget Status"}
              </h3>

              <span
                className={`text-xs px-2.5 py-0.5 rounded-full font-bold shadow-sm ${
                  isOver
                    ? "bg-rose-500/20 text-rose-300 border border-rose-500/35"
                    : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/35"
                }`}
              >
                {utilization}% Utilized
              </span>

              {/* Mode Toggle Pills */}
              <div className="inline-flex rounded-lg bg-black/40 p-0.5 border border-white/10 text-[11px] font-semibold">
                <button
                  type="button"
                  onClick={() => onToggleViewMode("monthly")}
                  className={`px-2.5 py-0.5 rounded-md transition-all ${
                    isMonthly
                      ? "bg-phonepe-purple text-white shadow-sm"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Monthly View
                </button>
                <button
                  type="button"
                  onClick={() => onToggleViewMode("yearly")}
                  className={`px-2.5 py-0.5 rounded-md transition-all ${
                    !isMonthly
                      ? "bg-phonepe-purple text-white shadow-sm"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Yearly View
                </button>
              </div>
            </div>

            <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
              {isMonthly ? (
                isOverMonthlyBudget ? (
                  <>
                    You have spent <span className="font-bold text-white">{formatINR(totalSpent)}</span> against your monthly target of{" "}
                    <span className="font-bold text-white">{formatINR(monthlyBudget)}</span>. Exceeded by{" "}
                    <span className="font-extrabold text-rose-300 underline underline-offset-2">
                      +{formatINR(overAmount)}
                    </span>
                    .
                  </>
                ) : (
                  <>
                    You have spent <span className="font-bold text-white">{formatINR(totalSpent)}</span> of your{" "}
                    <span className="font-bold text-white">{formatINR(monthlyBudget)}</span> monthly budget. Safe remaining balance:{" "}
                    <span className="font-bold text-emerald-300">
                      {formatINR(Math.max(0, monthlyBudget - totalSpent))}
                    </span>
                    .
                  </>
                )
              ) : (
                isOverYearlyBudget ? (
                  <>
                    Total recorded spending is <span className="font-bold text-white">{formatINR(totalSpent)}</span> against your yearly budget of{" "}
                    <span className="font-bold text-white">{formatINR(yearlyBudget)}</span>. Exceeded annual budget by{" "}
                    <span className="font-extrabold text-rose-300">+{formatINR(overAmount)}</span>.
                  </>
                ) : (
                  <>
                    You have spent <span className="font-bold text-white">{formatINR(totalSpent)}</span> out of your{" "}
                    <span className="font-bold text-white">{formatINR(yearlyBudget)}</span> annual limit (
                    <span className="text-emerald-300 font-semibold">{formatINR(Math.max(0, yearlyBudget - totalSpent))} buffer remaining</span>).
                    {projectedOneYear && projectedOneYear > 0 && (
                      <span className="block sm:inline sm:ml-1 text-slate-400">
                        At this pace, your 1-year projected spend is{" "}
                        <strong className="text-phonepe-light font-mono">{formatINR(projectedOneYear)}</strong>.
                      </span>
                    )}
                  </>
                )
              )}
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="hidden sm:flex flex-col items-end">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
              {isMonthly ? "Monthly Target" : "Annual Target"}
            </span>
            <span className="text-sm font-bold text-slate-100 font-mono">
              {formatINR(activeLimit)}
            </span>
          </div>

          <button
            type="button"
            onClick={onEditBudget}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/15 text-xs font-semibold text-slate-200 hover:text-white transition-all shadow-md active:scale-95 cursor-pointer"
          >
            <Sliders className="w-3.5 h-3.5 text-phonepe-accent" />
            <span>Manage Budget</span>
          </button>
        </div>
      </div>

      {/* Progress Bar with Dual Gauge Indicator */}
      <div className="mt-4 w-full bg-slate-900/90 rounded-full h-2 overflow-hidden border border-white/10">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            isOver
              ? "bg-gradient-to-r from-rose-500 via-red-500 to-rose-400 shadow-[0_0_12px_rgba(244,63,94,0.6)]"
              : "bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-300 shadow-[0_0_12px_rgba(16,185,129,0.6)]"
          }`}
          style={{ width: `${Math.min(100, utilization)}%` }}
        />
      </div>
    </div>
  );
};
