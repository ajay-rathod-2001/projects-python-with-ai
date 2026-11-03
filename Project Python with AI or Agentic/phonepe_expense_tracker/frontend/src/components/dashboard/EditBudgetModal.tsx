import React, { useState, useEffect } from "react";
import { Sliders, X, Calendar, Sparkles } from "lucide-react";
import { formatINR } from "../../lib/formatters";

interface EditBudgetModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentMonthlyBudget: number;
  currentYearlyBudget: number;
  onSave: (monthlyBudget: number, yearlyBudget: number) => void;
}

export const EditBudgetModal: React.FC<EditBudgetModalProps> = ({
  isOpen,
  onClose,
  currentMonthlyBudget,
  currentYearlyBudget,
  onSave,
}) => {
  const [monthlyInput, setMonthlyInput] = useState<string>(currentMonthlyBudget.toString());
  const [yearlyInput, setYearlyInput] = useState<string>(currentYearlyBudget.toString());
  const [autoSyncYearly, setAutoSyncYearly] = useState<boolean>(true);

  useEffect(() => {
    setMonthlyInput(currentMonthlyBudget.toString());
    setYearlyInput(currentYearlyBudget.toString());
  }, [currentMonthlyBudget, currentYearlyBudget, isOpen]);

  if (!isOpen) return null;

  const handleMonthlyChange = (val: string) => {
    setMonthlyInput(val);
    const num = parseFloat(val);
    if (autoSyncYearly && !isNaN(num) && num > 0) {
      setYearlyInput((num * 12).toString());
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const m = parseFloat(monthlyInput);
    const y = parseFloat(yearlyInput);
    if (!isNaN(m) && m > 0) {
      const finalY = !isNaN(y) && y > 0 ? y : m * 12;
      onSave(m, finalY);
      onClose();
    }
  };

  const applyPreset = (monthlyPreset: number) => {
    setMonthlyInput(monthlyPreset.toString());
    if (autoSyncYearly) {
      setYearlyInput((monthlyPreset * 12).toString());
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-in fade-in duration-200">
      <div className="glass-card rounded-2xl border border-phonepe-border w-full max-w-lg p-6 shadow-2xl relative">
        <div className="flex items-center justify-between border-b border-white/10 pb-3.5 mb-5">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-phonepe-purple/20 border border-phonepe-accent/30 text-phonepe-light">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-wide">
                Configure Budget Targets
              </h3>
              <p className="text-[11px] text-slate-400">
                Set and customize your Monthly & Annual spending thresholds
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Quick Presets */}
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
              Quick Monthly Presets
            </span>
            <div className="grid grid-cols-5 gap-1.5">
              {[5000, 10000, 15000, 25000, 50000].map((preset) => (
                <button
                  type="button"
                  key={preset}
                  onClick={() => applyPreset(preset)}
                  className={`py-1.5 px-2 rounded-lg text-xs font-semibold border transition-all ${
                    parseFloat(monthlyInput) === preset
                      ? "bg-phonepe-purple text-white border-phonepe-accent shadow-md shadow-purple-900/40"
                      : "bg-white/5 hover:bg-white/10 text-slate-300 border-white/5"
                  }`}
                >
                  ₹{(preset / 1000).toFixed(0)}k
                </button>
              ))}
            </div>
          </div>

          {/* Monthly Budget Input */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
              <span>Monthly Budget Target</span>
              <span className="text-slate-400 font-mono text-[11px]">
                Current: {formatINR(currentMonthlyBudget)}
              </span>
            </label>
            <div className="relative">
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-sm">
                ₹
              </span>
              <input
                type="number"
                step="500"
                min="100"
                value={monthlyInput}
                onChange={(e) => handleMonthlyChange(e.target.value)}
                className="w-full bg-phonepe-darker/90 border border-white/15 rounded-xl pl-9 pr-4 py-2.5 text-sm font-bold text-white focus:outline-none focus:border-phonepe-accent"
                autoFocus
              />
            </div>
          </div>

          {/* Yearly Budget Input */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-phonepe-light" />
                <span>Annual / Yearly Budget Target</span>
              </label>
              <button
                type="button"
                onClick={() => {
                  setAutoSyncYearly(!autoSyncYearly);
                  if (!autoSyncYearly && parseFloat(monthlyInput) > 0) {
                    setYearlyInput((parseFloat(monthlyInput) * 12).toString());
                  }
                }}
                className="text-[10px] text-phonepe-light hover:underline flex items-center gap-1"
              >
                <Sparkles className="w-3 h-3" />
                <span>{autoSyncYearly ? "Auto 12x Linked" : "Custom Manual"}</span>
              </button>
            </div>
            <div className="relative">
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-sm">
                ₹
              </span>
              <input
                type="number"
                step="5000"
                min="1000"
                value={yearlyInput}
                onChange={(e) => {
                  setAutoSyncYearly(false);
                  setYearlyInput(e.target.value);
                }}
                className="w-full bg-phonepe-darker/90 border border-white/15 rounded-xl pl-9 pr-4 py-2.5 text-sm font-bold text-white focus:outline-none focus:border-phonepe-accent"
              />
            </div>
            <div className="text-[11px] text-slate-400 flex items-center justify-between pt-0.5">
              <span>Annual Cap:</span>
              <span className="font-semibold text-slate-200">{formatINR(parseFloat(yearlyInput) || 0)}</span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="pt-3 flex items-center justify-end gap-2.5 border-t border-white/10">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-semibold text-slate-300 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-phonepe-purple hover:bg-purple-600 text-xs font-bold text-white transition-all shadow-lg shadow-purple-900/40"
            >
              Save Budget Limits
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
