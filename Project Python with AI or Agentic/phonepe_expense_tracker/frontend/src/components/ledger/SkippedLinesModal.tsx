import React from "react";
import { AlertTriangle, X } from "lucide-react";
import { SkippedLine } from "../../types/expense";

interface SkippedLinesModalProps {
  isOpen: boolean;
  onClose: () => void;
  skippedLines: SkippedLine[];
}

export const SkippedLinesModal: React.FC<SkippedLinesModalProps> = ({
  isOpen,
  onClose,
  skippedLines,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="glass-card rounded-2xl border border-phonepe-border w-full max-w-lg p-5 shadow-2xl relative">
        <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
          <div className="flex items-center gap-2 text-amber-400">
            <AlertTriangle className="w-5 h-5" />
            <h3 className="text-sm font-bold tracking-wide">
              Data Integrity Diagnostics
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <p className="text-xs text-slate-300 mb-3">
          The parser detected <strong>{skippedLines.length}</strong> line(s) with formatting issues. These lines were skipped safely to protect aggregate calculation accuracy:
        </p>

        <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
          {skippedLines.map((item, idx) => (
            <div
              key={idx}
              className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 text-xs"
            >
              <div className="flex items-center justify-between text-amber-300 font-semibold mb-1">
                <span>Line #{item.line_number}</span>
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/30">
                  Syntax Warning
                </span>
              </div>
              <div className="font-mono bg-black/40 p-1.5 rounded text-slate-200 text-[11px] mb-1 break-all">
                {item.raw_content}
              </div>
              <div className="text-[11px] text-slate-400">
                <span className="text-amber-400 font-medium">Issue:</span> {item.reason}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-5 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-phonepe-purple hover:bg-purple-600 text-xs font-semibold text-white transition-colors"
          >
            Done Reviewing
          </button>
        </div>
      </div>
    </div>
  );
};

