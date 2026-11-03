import React, { useState, useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
  ReferenceLine,
} from "recharts";
import {
  CalendarDays,
  TrendingUp,
  Sparkles,
  ShieldAlert,
  ChevronDown,
  X,
  Filter,
} from "lucide-react";
import { ExpenseForecast } from "../../types/expense";
import { formatINR } from "../../lib/formatters";

interface FinancialRunwayAndMonthsProps {
  monthlyBreakdown: Record<string, number>;
  yearlyBreakdown: Record<string, number>;
  forecast?: ExpenseForecast;
  monthlyBudget: number;
  yearlyBudget: number;
  selectedMonth: string; // "all" or "YYYY-MM"
  onSelectMonth: (month: string) => void;
}

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
];

const MONTH_FULL_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

export const FinancialRunwayAndMonths: React.FC<FinancialRunwayAndMonthsProps> = ({
  monthlyBreakdown,
  yearlyBreakdown,
  forecast,
  monthlyBudget,
  yearlyBudget,
  selectedMonth,
  onSelectMonth,
}) => {
  const [activeForecastTab, setActiveForecastTab] = useState<"3m" | "6m" | "1y" | "2y" | "5y">("1y");

  // Determine available years from monthly/yearly breakdowns
  const availableYears = useMemo(() => {
    const years = new Set<string>();
    Object.keys(yearlyBreakdown).forEach((y) => years.add(y));
    Object.keys(monthlyBreakdown).forEach((m) => {
      const parts = m.split("-");
      if (parts[0]) years.add(parts[0]);
    });
    const arr = Array.from(years);
    return arr.length > 0 ? arr.sort() : ["2026"];
  }, [yearlyBreakdown, monthlyBreakdown]);

  // Selected Year for the quick calendar view
  const [selectedYear, setSelectedYear] = useState<string>(
    availableYears[availableYears.length - 1] || "2026"
  );

  // List of recorded months that actually have data
  const recordedMonthOptions = useMemo(() => {
    return Object.entries(monthlyBreakdown)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, amount]) => {
        const parts = key.split("-");
        const monthIndex = parts.length === 2 ? parseInt(parts[1], 10) - 1 : 0;
        const name = MONTH_FULL_NAMES[monthIndex] || key;
        const year = parts[0] || "";
        return {
          key,
          label: `${name} ${year}`,
          amount,
        };
      });
  }, [monthlyBreakdown]);

  // Format monthly data for the bar chart
  const monthsData = useMemo(() => {
    return Object.entries(monthlyBreakdown)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([monthKey, amount]) => {
        const parts = monthKey.split("-");
        const monthIndex = parts.length === 2 ? parseInt(parts[1], 10) - 1 : 0;
        const monthLabel =
          parts.length === 2
            ? `${MONTH_NAMES[monthIndex]} '${parts[0].slice(2)}`
            : monthKey;

        const isOver = amount > monthlyBudget;

        return {
          monthKey,
          monthLabel,
          amount,
          isOver,
        };
      });
  }, [monthlyBreakdown, monthlyBudget]);

  const dailyAvg = forecast?.daily_average || 0;
  const proj3M = forecast?.projected_3_months || dailyAvg * 90;
  const proj6M = forecast?.projected_6_months || dailyAvg * 180;
  const proj1Y = forecast?.projected_1_year || dailyAvg * 365;
  const proj2Y = forecast?.projected_2_years || dailyAvg * 730;
  const proj5Y = forecast?.projected_5_years || dailyAvg * 1825;

  const forecastScenarios = [
    {
      id: "3m",
      title: "3 Months Later",
      period: "Quarterly Outlook (90 Days)",
      amount: proj3M,
      budgetRef: monthlyBudget * 3,
      multiplier: "3M",
    },
    {
      id: "6m",
      title: "6 Months Later",
      period: "Half-Year Outlook (180 Days)",
      amount: proj6M,
      budgetRef: monthlyBudget * 6,
      multiplier: "6M",
    },
    {
      id: "1y",
      title: "1 Year Later",
      period: "Annual Capital Outflow (365 Days)",
      amount: proj1Y,
      budgetRef: yearlyBudget,
      multiplier: "1Y",
    },
    {
      id: "2y",
      title: "2 Years Later",
      period: "Biennial Projection (730 Days)",
      amount: proj2Y,
      budgetRef: yearlyBudget * 2,
      multiplier: "2Y",
    },
    {
      id: "5y",
      title: "5 Years Later",
      period: "Long-Term Wealth Impact (1,825 Days)",
      amount: proj5Y,
      budgetRef: yearlyBudget * 5,
      multiplier: "5Y",
    },
  ];

  const activeScenario =
    forecastScenarios.find((s) => s.id === activeForecastTab) || forecastScenarios[2];

  const CustomBarTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="glass-card rounded-xl p-3.5 shadow-2xl border border-white/10 text-xs">
          <div className="font-extrabold text-white text-sm mb-1">{data.monthLabel} ({data.monthKey})</div>
          <div className="text-base font-extrabold text-phonepe-light font-mono">{formatINR(data.amount)}</div>
          <div className="text-[11px] text-slate-300 mt-1 flex items-center justify-between gap-3">
            <span>Budget Target:</span>
            <span className="font-semibold text-slate-200">{formatINR(monthlyBudget)}</span>
          </div>
          {data.isOver ? (
            <div className="text-[11px] font-bold text-rose-400 mt-1 flex items-center gap-1">
              <span>⚠️ Over Budget by +{formatINR(data.amount - monthlyBudget)}</span>
            </div>
          ) : (
            <div className="text-[11px] font-bold text-emerald-400 mt-1">
              ✓ Within Budget ({formatINR(monthlyBudget - data.amount)} buffer)
            </div>
          )}
          <div className="text-[10px] text-slate-400 mt-1.5 italic">Click bar to filter entire dashboard to this month</div>
        </div>
      );
    }
    return null;
  };

  const handleMonthPillClick = (monthNum: string, hasData: boolean) => {
    if (!hasData) {
      return; // Prevent clicking months that have 0 transactions
    }
    const key = `${selectedYear}-${monthNum}`;
    if (selectedMonth === key) {
      onSelectMonth("all");
    } else {
      onSelectMonth(key);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* 1. Monthly Expense Breakdown & Robust Chooser */}
      <div className="glass-card rounded-2xl p-5 border border-phonepe-border flex flex-col justify-between">
        <div>
          {/* Header & Controls */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-phonepe-purple/20 border border-phonepe-purple/30 flex items-center justify-center text-phonepe-light">
                <CalendarDays className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  Monthly Expense Breakdown
                </h3>
                <span className="text-[11px] text-slate-400">
                  Filter dashboard by specific Month & Year
                </span>
              </div>
            </div>

            {/* Direct Month Selector Dropdown */}
            <div className="flex items-center gap-2">
              <div className="relative">
                <select
                  value={selectedMonth}
                  onChange={(e) => onSelectMonth(e.target.value)}
                  className="bg-phonepe-darker/90 border border-phonepe-accent/40 rounded-xl px-3 py-1.5 text-xs font-bold text-white focus:outline-none focus:border-phonepe-light cursor-pointer pr-7 appearance-none shadow-sm"
                >
                  <option value="all" className="bg-slate-900 text-white font-bold">
                    📅 All Months ({recordedMonthOptions.length} Recorded)
                  </option>
                  {recordedMonthOptions.map((opt) => (
                    <option key={opt.key} value={opt.key} className="bg-slate-900 text-white">
                      {opt.label} • {formatINR(opt.amount)}
                    </option>
                  ))}
                </select>
                <ChevronDown className="w-3.5 h-3.5 text-phonepe-light absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>

              {selectedMonth !== "all" && (
                <button
                  type="button"
                  onClick={() => onSelectMonth("all")}
                  className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-semibold hover:bg-rose-500/30 transition-colors cursor-pointer"
                  title="Reset filter to show all months"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Reset</span>
                </button>
              )}
            </div>
          </div>

          {/* Quick Calendar Matrix (Only enables months that have data!) */}
          <div className="mb-3.5 bg-black/30 p-2.5 rounded-xl border border-white/5">
            <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 px-1 flex-wrap gap-1">
              <div className="flex items-center gap-1.5">
                <Filter className="w-3 h-3 text-phonepe-accent" />
                <span>Quick Select Month:</span>
                {availableYears.length > 1 && (
                  <div className="flex items-center gap-1 ml-1">
                    {availableYears.map((yr) => (
                      <button
                        key={yr}
                        type="button"
                        onClick={() => setSelectedYear(yr)}
                        className={`px-2 py-0.5 rounded text-[10px] font-bold transition-all cursor-pointer ${
                          selectedYear === yr
                            ? "bg-phonepe-purple text-white shadow-sm ring-1 ring-purple-400/40"
                            : "bg-white/5 text-slate-400 hover:text-white hover:bg-white/10"
                        }`}
                      >
                        {yr}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              {selectedMonth !== "all" ? (
                <span className="text-phonepe-light font-mono font-bold bg-phonepe-purple/30 px-2 py-0.5 rounded-md border border-purple-500/30">
                  Active: {selectedMonth}
                </span>
              ) : (
                <span className="text-slate-400 font-normal">
                  Showing All Months
                </span>
              )}
            </div>

            <div className="grid grid-cols-6 sm:grid-cols-12 gap-1">
              {MONTH_NAMES.map((name, idx) => {
                const monthNum = String(idx + 1).padStart(2, "0");
                const monthKey = `${selectedYear}-${monthNum}`;
                const hasData = Boolean(monthlyBreakdown[monthKey]);
                const isSelected = selectedMonth === monthKey;
                const isOver = (monthlyBreakdown[monthKey] || 0) > monthlyBudget;

                return (
                  <button
                    type="button"
                    key={monthNum}
                    disabled={!hasData}
                    onClick={() => handleMonthPillClick(monthNum, hasData)}
                    className={`py-1.5 px-1 rounded-lg text-[10px] font-bold transition-all text-center relative ${
                      isSelected
                        ? "bg-phonepe-accent text-white shadow-lg shadow-purple-500/40 ring-1 ring-white"
                        : hasData
                        ? isOver
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30 cursor-pointer"
                          : "bg-purple-500/20 text-purple-200 border border-purple-500/40 hover:bg-purple-500/30 cursor-pointer"
                        : "bg-white/[0.02] text-slate-600 border border-transparent opacity-35 cursor-not-allowed"
                    }`}
                    title={
                      hasData
                        ? `${MONTH_FULL_NAMES[idx]} ${selectedYear}: ${formatINR(monthlyBreakdown[monthKey])} (Click to filter / unfilter)`
                        : `${MONTH_FULL_NAMES[idx]} ${selectedYear}: No transactions recorded`
                    }
                  >
                    <span>{name}</span>
                    {hasData && (
                      <span
                        className={`absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full ${
                          isOver ? "bg-rose-400 shadow-sm shadow-rose-400/50" : "bg-emerald-400 shadow-sm shadow-emerald-400/50"
                        }`}
                      />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Month Bar Chart with Constrained Bar Sizes & Ambient Glow */}
          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={monthsData}
                barCategoryGap="20%"
                margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
                <XAxis
                  dataKey="monthLabel"
                  tickLine={false}
                  axisLine={false}
                  tick={{ fill: "#94A3B8", fontSize: 11, fontWeight: 500 }}
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  tick={{ fill: "#94A3B8", fontSize: 10 }}
                  tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                />
                {/* Budget Reference Line */}
                <ReferenceLine
                  y={monthlyBudget}
                  stroke="#F59E0B"
                  strokeDasharray="4 4"
                  strokeWidth={1.5}
                  label={{
                    value: `Limit: ₹${(monthlyBudget / 1000).toFixed(0)}k`,
                    fill: "#F59E0B",
                    fontSize: 9,
                    position: "insideTopRight",
                  }}
                />
                {/* Custom tooltip without gray box */}
                <Tooltip
                  cursor={{ fill: "rgba(139, 92, 246, 0.08)", radius: 8 }}
                  content={<CustomBarTooltip />}
                />
                <Bar
                  dataKey="amount"
                  maxBarSize={44}
                  radius={[6, 6, 0, 0]}
                  cursor="pointer"
                  onClick={(data: any) => {
                    const key = data?.monthKey || (data?.payload && data.payload.monthKey);
                    if (key) {
                      if (selectedMonth === key) {
                        onSelectMonth("all");
                      } else {
                        onSelectMonth(key);
                      }
                    }
                  }}
                >
                  {monthsData.map((entry) => (
                    <Cell
                      key={`bar-${entry.monthKey}`}
                      fill={
                        entry.monthKey === selectedMonth
                          ? "#A78BFA"
                          : entry.isOver
                          ? "#F43F5E"
                          : "#8B5CF6"
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Footer Info Row */}
        <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between text-xs">
          <div className="flex items-center gap-3">
            <div>
              <span className="text-slate-400">Recorded Months: </span>
              <span className="font-bold text-white font-mono">{monthsData.length}</span>
            </div>
            {availableYears.length > 0 && (
              <div>
                <span className="text-slate-400">• Years: </span>
                <span className="font-bold text-slate-200 font-mono">
                  {availableYears.join(", ")}
                </span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            {monthsData.some((m) => m.isOver) ? (
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-400 bg-rose-500/10 px-2.5 py-0.5 rounded-full border border-rose-500/20">
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>Over Budget Detected</span>
              </span>
            ) : (
              <span className="text-emerald-400 font-semibold text-[11px]">
                Within limits
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 2. Predictive Financial Runway & Forecast Engine (3M, 6M, 1Y, 2Y, 5Y) */}
      <div className="glass-card rounded-2xl p-5 border border-phonepe-border flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <TrendingUp className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  Predictive Expense Forecast
                </h3>
                <span className="text-[11px] text-slate-400">
                  Based on daily burn rate of{" "}
                  <strong className="text-slate-200 font-mono">{formatINR(dailyAvg)}/day</strong>
                </span>
              </div>
            </div>

            <div className="p-1 rounded-full bg-white/5 border border-white/10 text-phonepe-light">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* Forecast Timeframe Selector Pills */}
          <div className="grid grid-cols-5 gap-1 mb-3.5 p-1 rounded-xl bg-black/40 border border-white/5">
            {forecastScenarios.map((s) => (
              <button
                type="button"
                key={s.id}
                onClick={() => setActiveForecastTab(s.id as any)}
                className={`py-1.5 rounded-lg text-[11px] font-bold transition-all text-center cursor-pointer ${
                  activeForecastTab === s.id
                    ? "bg-phonepe-purple text-white shadow-md shadow-purple-900/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {s.multiplier}
              </button>
            ))}
          </div>

          {/* Active Forecast Spotlight Card */}
          <div className="p-4 rounded-xl bg-gradient-to-br from-purple-950/30 to-indigo-950/20 border border-purple-500/20 relative overflow-hidden">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="font-bold text-slate-300">{activeScenario.title}</span>
              <span className="text-[10px] text-slate-400">{activeScenario.period}</span>
            </div>

            <div className="text-2xl font-extrabold text-white tracking-tight mt-1 font-mono">
              {formatINR(activeScenario.amount)}
            </div>

            {/* Comparison vs Budget target for that period */}
            <div className="mt-2 text-xs flex items-center justify-between text-slate-300 pt-2 border-t border-white/10">
              <span className="text-slate-400">Budget Target ({activeScenario.multiplier}):</span>
              <span className="font-semibold text-slate-200 font-mono">
                {formatINR(activeScenario.budgetRef)}
              </span>
            </div>

            <div className="mt-1 text-[11px] flex items-center justify-between">
              <span className="text-slate-400">Projected Variance:</span>
              {activeScenario.amount > activeScenario.budgetRef ? (
                <span className="font-bold text-rose-400">
                  +{formatINR(activeScenario.amount - activeScenario.budgetRef)} over target
                </span>
              ) : (
                <span className="font-bold text-emerald-400">
                  {formatINR(activeScenario.budgetRef - activeScenario.amount)} buffer remaining
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Forecast Summary Matrix */}
        <div className="mt-3 pt-3 border-t border-white/5 grid grid-cols-3 gap-2 text-center">
          <div className="p-2 rounded-lg bg-white/[0.02] border border-white/5">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">3-Month Outflow</div>
            <div className="text-xs font-bold text-slate-200 font-mono mt-0.5">{formatINR(proj3M)}</div>
          </div>
          <div className="p-2 rounded-lg bg-white/[0.02] border border-white/5">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">6-Month Outflow</div>
            <div className="text-xs font-bold text-slate-200 font-mono mt-0.5">{formatINR(proj6M)}</div>
          </div>
          <div className="p-2 rounded-lg bg-white/[0.02] border border-white/5">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">1-Year Outflow</div>
            <div className="text-xs font-bold text-phonepe-light font-mono mt-0.5">{formatINR(proj1Y)}</div>
          </div>
        </div>
      </div>
    </div>
  );
};
