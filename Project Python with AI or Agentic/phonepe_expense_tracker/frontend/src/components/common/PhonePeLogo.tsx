import React from "react";

interface PhonePeLogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

export const PhonePeLogo: React.FC<PhonePeLogoProps> = ({ size = "md", className = "" }) => {
  const sizeMap = {
    sm: "w-6 h-6 text-[10px]",
    md: "w-9 h-9 text-xs",
    lg: "w-12 h-12 text-sm",
    xl: "w-16 h-16 text-lg",
  };

  const dimMap = {
    sm: { w: 24, h: 24, r: 6 },
    md: { w: 36, h: 36, r: 10 },
    lg: { w: 48, h: 48, r: 14 },
    xl: { w: 64, h: 64, r: 18 },
  };

  const dim = dimMap[size];

  return (
    <div
      className={`relative inline-flex items-center justify-center flex-shrink-0 select-none group ${sizeMap[size]} ${className}`}
    >
      {/* Outer ambient glow */}
      <div className="absolute inset-0 rounded-2xl bg-phonepe-purple blur-md opacity-40 group-hover:opacity-75 transition-opacity" />

      {/* SVG Icon */}
      <svg
        width={dim.w}
        height={dim.h}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="relative z-10 drop-shadow-md"
      >
        <defs>
          <linearGradient id="phonepeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#7C3AED" />
            <stop offset="45%" stopColor="#5F259F" />
            <stop offset="100%" stopColor="#3B0764" />
          </linearGradient>
          <linearGradient id="goldDot" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FDE047" />
            <stop offset="100%" stopColor="#EAB308" />
          </linearGradient>
        </defs>

        {/* Squircle Badge */}
        <rect
          x="2"
          y="2"
          width="60"
          height="60"
          rx={dim.r * 1.8}
          fill="url(#phonepeGrad)"
          stroke="rgba(255,255,255,0.18)"
          strokeWidth="1.5"
        />

        {/* Iconic Stylized Devanagari 'Pe' (पे) Symbol in White */}
        {/* Top Horizontal Bar */}
        <path
          d="M18 19H46C47.1 19 48 19.9 48 21C48 22.1 47.1 23 46 23H18C16.9 23 16 22.1 16 21C16 19.9 16.9 19 18 19Z"
          fill="white"
        />

        {/* Main Vertical Stem */}
        <path
          d="M37 21V47C37 48.1 36.1 49 35 49C33.9 49 33 48.1 33 47V21H37Z"
          fill="white"
        />

        {/* Rounded Loop (Pa curve) */}
        <path
          d="M23 23V32C23 35.866 26.134 39 30 39H34V35H30C28.3431 35 27 33.6569 27 32V23H23Z"
          fill="white"
        />

        {/* Matra Accent / Flow */}
        <path
          d="M37 21C37 21 42 14 45 13C45.8 12.7 46.5 13.5 46.1 14.3C44.5 17.5 39 21 39 21H37Z"
          fill="white"
        />

        {/* Gold Trust Sparkle Accent */}
        <circle cx="46" cy="46" r="3.5" fill="url(#goldDot)" />
      </svg>
    </div>
  );
};

