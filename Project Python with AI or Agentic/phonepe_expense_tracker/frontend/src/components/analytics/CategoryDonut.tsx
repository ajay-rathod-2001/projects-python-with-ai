import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { CATEGORY_COLORS, DEFAULT_COLOR } from "../../lib/constants";
import { formatINR } from "../../lib/formatters";

interface CategoryDonutProps {
  categoryTotals: Record<string, number>;
  totalSpent: number;
}

export const CategoryDonut: React.FC<CategoryDonutProps> = ({
  categoryTotals,
  totalSpent,
}) => {
  const chartData = Object.entries(categoryTotals).map(([name, value]) => ({
    name,
    value,
    share: totalSpent > 0 ? ((value / totalSpent) * 100).toFixed(1) : "0",
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const colorToken = CATEGORY_COLORS[data.name] || DEFAULT_COLOR;
      return (
        <div className="glass-card rounded-lg p-2.5 shadow-xl border border-white/10 text-xs">
          <div className="flex items-center gap-2 mb-1">
            <span
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: colorToken.fill }}
            />
            <span className="font-bold text-white">{data.name}</span>
          </div>
          <div className="text-slate-300 font-semibold">{formatINR(data.value)}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">{data.share}% of total spend</div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-card rounded-xl p-4.5 border border-phonepe-border flex flex-col h-full">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
          Spending Breakdown by Category
        </h3>
        <span className="text-[10px] text-slate-400 font-medium">
          {chartData.length} Categories
        </span>
      </div>

      {chartData.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-xs text-slate-400">
          <p>No category expenses recorded for this selection.</p>
        </div>
      ) : (
        <div className="flex-1 flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Recharts Pie Donut */}
          <div className="relative w-full md:w-1/2 h-52 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Tooltip content={<CustomTooltip />} />
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="rgba(17, 24, 39, 0.8)"
                  strokeWidth={2}
                >
                  {chartData.map((entry) => {
                    const color = CATEGORY_COLORS[entry.name] || DEFAULT_COLOR;
                    return <Cell key={`cell-${entry.name}`} fill={color.fill} />;
                  })}
                </Pie>
              </PieChart>
            </ResponsiveContainer>

            {/* Donut Center Display */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-[10px] font-semibold uppercase text-slate-400">Total</span>
              <span className="text-sm font-bold text-white tracking-tight">
                {formatINR(totalSpent)}
              </span>
            </div>
          </div>

          {/* Breakdown Legend List */}
          <div className="w-full md:w-1/2 flex flex-col gap-2 max-h-52 overflow-y-auto pr-1">
            {chartData.map((item) => {
              const color = CATEGORY_COLORS[item.name] || DEFAULT_COLOR;
              return (
                <div
                  key={item.name}
                  className="flex items-center justify-between p-2 rounded-lg bg-white/[0.02] hover:bg-white/[0.05] border border-white/5 transition-colors text-xs"
                >
                  <div className="flex items-center gap-2">
                    <span
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      style={{ backgroundColor: color.fill }}
                    />
                    <span className="font-medium text-slate-200">{item.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white">{formatINR(item.value)}</span>
                    <span className="text-[10px] text-slate-400 w-9 text-right font-mono">
                      {item.share}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

