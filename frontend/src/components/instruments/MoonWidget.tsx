import type { FC } from 'react';

export interface MoonWidgetProps {
  phaseName?: string;
  illuminationPct?: number;
  ageDays?: number;
  className?: string;
}

export const MoonWidget: FC<MoonWidgetProps> = ({
  phaseName = 'Waxing Gibbous',
  illuminationPct = 78,
  ageDays = 10.4,
  className = '',
}) => {
  return (
    <div className={`bg-[#131720] border border-[#1A1F2B] rounded-xl p-4 flex flex-col items-center justify-between select-none ${className}`}>
      <span className="text-[10px] font-mono text-[#5A6475] uppercase tracking-wider">
        LUNAR OBSERVATORY
      </span>

      {/* Moon Phase Rendering Scope */}
      <div className="relative w-24 h-24 my-2 flex items-center justify-center">
        <svg viewBox="0 0 100 100" className="w-full h-full filter drop-shadow-[0_0_12px_rgba(255,255,255,0.2)]">
          {/* Base Moon Shadow */}
          <circle cx="50" cy="50" r="42" fill="#0C0E12" stroke="#242C3A" strokeWidth="1" />

          {/* Illuminated Moon Arc */}
          <path
            d="M 50 8 A 42 42 0 0 1 50 92 A 28 42 0 0 0 50 8 Z"
            fill="#E5E7EB"
            opacity="0.9"
          />

          {/* Lunar Crater Details */}
          <circle cx="62" cy="35" r="4" fill="#D1D5DB" opacity="0.4" />
          <circle cx="70" cy="52" r="6" fill="#D1D5DB" opacity="0.3" />
          <circle cx="58" cy="68" r="3" fill="#D1D5DB" opacity="0.5" />
        </svg>
      </div>

      <div className="text-center font-mono">
        <div className="font-['Outfit'] font-semibold text-sm text-white">{phaseName}</div>
        <div className="text-xs text-[#47F3A0] font-bold mt-0.5">{illuminationPct}% ILLUMINATED</div>
        <div className="text-[10px] text-[#5A6475] font-normal">AGE: {ageDays.toFixed(1)} DAYS</div>
      </div>
    </div>
  );
};
