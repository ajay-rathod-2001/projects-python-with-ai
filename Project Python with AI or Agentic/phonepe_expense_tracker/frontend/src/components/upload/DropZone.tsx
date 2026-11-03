import React, { useState, useRef } from "react";
import { UploadCloud, CheckCircle, FolderOpen, RefreshCw, FileSpreadsheet } from "lucide-react";
import * as XLSX from "xlsx";
import { PhonePeLogo } from "../common/PhonePeLogo";

interface DropZoneProps {
  onFileLoaded: (content: string, filename: string) => void;
  onNativeBrowse: () => void;
  currentFilename?: string;
  isDesktop: boolean;
  isLoading?: boolean;
}

export const DropZone: React.FC<DropZoneProps> = ({
  onFileLoaded,
  onNativeBrowse,
  currentFilename,
  isDesktop,
  isLoading = false,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsHovered(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsHovered(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsHovered(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file: File) => {
    const ext = file.name.split(".").pop()?.toLowerCase();

    if (ext === "xlsx" || ext === "xls") {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const buffer = new Uint8Array(event.target?.result as ArrayBuffer);
          const workbook = XLSX.read(buffer, { type: "array" });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const csvText = XLSX.utils.sheet_to_csv(worksheet);
          onFileLoaded(csvText, file.name);
        } catch (err) {
          console.error("Excel parse error:", err);
          alert("Could not parse Excel workbook. Please verify columns: Date, Merchant, Amount.");
        }
      };
      reader.readAsArrayBuffer(file);
    } else {
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        if (content) {
          onFileLoaded(content, file.name);
        }
      };
      reader.onerror = () => {
        alert("Failed to read the file. Please ensure it is a valid text, CSV, or Excel file.");
      };
      reader.readAsText(file);
    }
  };

  const handleZoneClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleZoneClick}
      className={`relative cursor-pointer rounded-2xl border-2 transition-all duration-300 p-4.5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
        isHovered
          ? "border-phonepe-accent bg-purple-950/40 shadow-xl shadow-purple-950/40 scale-[1.008]"
          : "border-white/10 hover:border-phonepe-accent/50 bg-gradient-to-r from-phonepe-card/90 via-phonepe-dark/80 to-slate-900/90 shadow-lg"
      }`}
    >
      {/* Hidden file input supporting TXT, CSV, and EXCEL */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.csv,.xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/plain"
        className="hidden"
        onChange={handleFileInputChange}
      />

      {/* Left: PhonePe Logo & Upload Instructions */}
      <div className="flex items-center gap-3.5">
        <PhonePeLogo size="md" />

        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-bold text-white tracking-wide">
              Import Transactions Data
            </span>
            {currentFilename && (
              <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-emerald-300 bg-emerald-500/15 px-2.5 py-0.5 rounded-full border border-emerald-500/30 shadow-sm">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                <span>{currentFilename}</span>
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-1 flex items-center gap-1.5 flex-wrap">
            <span>Drag & drop your file anywhere:</span>
            <span className="text-phonepe-light font-mono bg-white/5 px-1.5 py-0.5 rounded border border-white/10">.txt</span>
            <span className="text-emerald-400 font-mono bg-white/5 px-1.5 py-0.5 rounded border border-white/10">.csv</span>
            <span className="text-blue-400 font-mono bg-white/5 px-1.5 py-0.5 rounded border border-white/10 flex items-center gap-1">
              <FileSpreadsheet className="w-3 h-3" />
              <span>.xlsx Excel</span>
            </span>
          </p>
        </div>
      </div>

      {/* Right: Quick Action Buttons */}
      <div className="flex items-center gap-2 self-end sm:self-center" onClick={(e) => e.stopPropagation()}>
        {isDesktop && (
          <button
            type="button"
            onClick={onNativeBrowse}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-phonepe-purple hover:bg-purple-600 border border-purple-400/30 text-xs font-semibold text-white shadow-lg shadow-purple-900/30 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
            title="Open native Windows file dialog"
          >
            {isLoading ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <FolderOpen className="w-3.5 h-3.5" />
            )}
            <span>Native Browse</span>
          </button>
        )}

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-200 hover:text-white transition-all shadow-sm active:scale-95 disabled:opacity-50"
          title="Select TXT, CSV, or Excel file"
        >
          <UploadCloud className="w-3.5 h-3.5 text-phonepe-accent" />
          <span>Upload File</span>
        </button>
      </div>
    </div>
  );
};
