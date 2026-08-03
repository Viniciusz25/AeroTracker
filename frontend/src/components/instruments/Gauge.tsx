import type { FC } from 'react';

export interface GaugeProps {
  label: string;
  value: number;
  min?: number;
  max?: number;
  unit?: string;
  className?: string;
}

export const Gauge: FC<GaugeProps> = ({
  label,
  value,
  min = 0,
  max = 100,
  unit = '',
  className = '',
}) => {
  const percentage = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));
  // Semi-circle arc length (r=40, circumference half = PI * 40 ≈ 125.66)
  const strokeDashoffset = 125.66 - (125.66 * percentage) / 100;

  return (
    <div
      className={`bg-[#131720] border border-[#1A1F2B] rounded-xl p-4 flex flex-col items-center justify-center select-none ${className}`}
    >
      <span className="text-[10px] font-mono text-[#5A6475] uppercase tracking-wider mb-1">
        {label}
      </span>

      <div className="relative w-32 h-20 flex items-end justify-center">
        <svg viewBox="0 0 100 60" className="w-full h-full">
          {/* Background Arc */}
          <path
            d="M 10 50 A 40 40 0 0 1 90 50"
            fill="none"
            stroke="#1A1F2B"
            strokeWidth="8"
            strokeLinecap="round"
          />
          {/* Colored Value Arc */}
          <path
            d="M 10 50 A 40 40 0 0 1 90 50"
            fill="none"
            stroke="#47F3A0"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray="125.66"
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-700 ease-out"
          />
        </svg>

        {/* Center Digital Value */}
        <div className="absolute bottom-1 flex items-baseline gap-1 font-mono">
          <span className="font-['Outfit'] font-bold text-xl text-white">
            {typeof value === 'number' ? value.toFixed(1) : value}
          </span>
          <span className="text-[10px] text-[#5A6475]">{unit}</span>
        </div>
      </div>

      <div className="w-full flex justify-between text-[9px] font-mono text-[#5A6475] mt-1 px-2">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
};
