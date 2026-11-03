import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { Transaction } from "../../types/expense";
import { formatINR } from "../../lib/formatters";

interface SpendVelocityProps {
  transactions: Transaction[];
}

export const SpendVelocity: React.FC<SpendVelocityProps> = ({ transactions }) => {
  // Aggregate transactions by date
  const dateMap: Record<string, number> = {};
  transactions.forEach((tx) => {
    dateMap[tx.date] = (dateMap[tx.date] || 0) + tx.amount;
  });

  const chartData = Object.entries(dateMap)
    .sort(([dateA], [dateB]) => dateA.localeCompare(dateB))
    .map(([date, amount]) => {
      // E.g. '2026-08-01' -> '01 Aug'
      const parts = date.split("-");
      const shortLabel = parts.length === 3 ? `${parts[2]}` : date;
      return {
        date,
        shortLabel,
        amount,
      };
    });

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="glass-card rounded-lg p-2.5 shadow-xl border border-white/10 text-xs">
          <div className="text-[11px] text-slate-400 font-mono mb-0.5">{data.date}</div>
          <div className="text-sm font-bold text-phonepe-light">{formatINR(data.amount)}</div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-card rounded-xl p-4.5 border border-phonepe-border flex flex-col h-full">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
          Daily Spend Velocity
        </h3>
        <span className="text-[10px] text-slate-400 font-medium">Daily Outflow Trend</span>
      </div>

      {chartData.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-xs text-slate-400">
          <p>No daily spending activity recorded for this selection.</p>
        </div>
      ) : (
        <div className="flex-1 w-full h-52">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="purpleGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
              <XAxis
                dataKey="shortLabel"
                tickLine={false}
                axisLine={false}
                tick={{ fill: "#94A3B8", fontSize: 10 }}
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tick={{ fill: "#94A3B8", fontSize: 10 }}
                tickFormatter={(val) => `₹${val}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="amount"
                stroke="#8B5CF6"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#purpleGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

