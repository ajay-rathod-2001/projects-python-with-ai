import React from "react";
import { UploadCloud, FileText, FileSpreadsheet } from "lucide-react";
import { PhonePeLogo } from "../common/PhonePeLogo";

interface GlobalDropOverlayProps {
  isDragging: boolean;
}

export const GlobalDropOverlay: React.FC<GlobalDropOverlayProps> = ({ isDragging }) => {
  if (!isDragging) return null;

  return (
    <div className="fixed inset-0 z-50 pointer-events-none flex flex-col items-center justify-center bg-phonepe-dark/90 backdrop-blur-md border-4 border-dashed border-phonepe-accent animate-in fade-in duration-200">
      <div className="relative flex flex-col items-center text-center p-8 max-w-lg">
        {/* Pulsing PhonePe Brand Logo */}
        <div className="relative mb-6">
          <div className="absolute inset-0 rounded-3xl bg-phonepe-accent/40 blur-2xl animate-pulse" />
          <PhonePeLogo size="xl" />
        </div>

        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-phonepe-purple/30 border border-phonepe-light/30 text-phonepe-light text-xs font-semibold mb-3">
          <UploadCloud className="w-4 h-4 animate-bounce" />
          <span>Release File to Analyze Instantly</span>
        </div>

        <h2 className="text-xl font-extrabold text-white tracking-wide">
          Drop PhonePe Transactions File
        </h2>
        <p className="text-xs text-slate-300 mt-2 max-w-md">
          Supports <code className="text-phonepe-light font-mono bg-white/10 px-1.5 py-0.5 rounded">.txt</code>,{" "}
          <code className="text-emerald-400 font-mono bg-white/10 px-1.5 py-0.5 rounded">.csv</code>, and{" "}
          <code className="text-blue-400 font-mono bg-white/10 px-1.5 py-0.5 rounded">.xlsx Excel</code> files. Automatic parsing, categorization, and budgeting will trigger immediately.
        </p>

        <div className="mt-6 flex items-center gap-3 text-[11px] text-slate-400 font-mono">
          <div className="flex items-center gap-1">
            <FileText className="w-3.5 h-3.5 text-phonepe-accent" />
            <span>TXT / CSV</span>
          </div>
          <span>•</span>
          <div className="flex items-center gap-1">
            <FileSpreadsheet className="w-3.5 h-3.5 text-blue-400" />
            <span>Excel Spreadsheet</span>
          </div>
        </div>
      </div>
    </div>
  );
};
