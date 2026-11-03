import React from "react";
import { Minus, Square, X } from "lucide-react";
import { PhonePeLogo } from "../common/PhonePeLogo";

interface TitleBarProps {
  onMinimize: () => void;
  onMaximize: () => void;
  onClose: () => void;
  isDesktop: boolean;
}

export const TitleBar: React.FC<TitleBarProps> = ({
  onMinimize,
  onMaximize,
  onClose,
  isDesktop,
}) => {
  return (
    <header className="h-11 bg-phonepe-darker/95 border-b border-phonepe-border flex items-center justify-between px-3.5 select-none z-50 flex-shrink-0">
      {/* Draggable Title Area */}
      <div className="pywebview-drag-region flex-1 h-full flex items-center gap-2.5 cursor-move">
        <PhonePeLogo size="sm" className="pointer-events-none" />
        <div className="flex items-center gap-2 pointer-events-none">
          <span className="text-xs font-extrabold tracking-wider text-white">
            PHONEPE <span className="text-phonepe-light font-normal">EXPENSE STUDIO</span>
          </span>
          <span className="text-[9px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-gradient-to-r from-purple-500/20 to-indigo-500/20 border border-purple-500/30 text-purple-300">
            {isDesktop ? "Enterprise Desktop" : "Web Preview"}
          </span>
        </div>
      </div>

      {/* Non-draggable Window Control Buttons */}
      <div className="flex items-center gap-1 z-50">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onMinimize();
          }}
          className="w-8 h-7 flex items-center justify-center rounded text-slate-400 hover:text-slate-100 hover:bg-white/10 transition-colors cursor-pointer"
          title="Minimize"
        >
          <Minus className="w-3.5 h-3.5" />
        </button>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onMaximize();
          }}
          className="w-8 h-7 flex items-center justify-center rounded text-slate-400 hover:text-slate-100 hover:bg-white/10 transition-colors cursor-pointer"
          title="Maximize"
        >
          <Square className="w-3 h-3" />
        </button>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onClose();
          }}
          className="w-8 h-7 flex items-center justify-center rounded text-slate-400 hover:text-white hover:bg-rose-600 transition-colors cursor-pointer"
          title="Close"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </header>
  );
};
