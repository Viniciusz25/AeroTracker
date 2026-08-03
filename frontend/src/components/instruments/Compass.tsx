import type { FC } from 'react';

export interface CompassProps {
  heading: number; // 0 to 359 degrees
  label?: string;
  size?: number;
  className?: string;
}

export const Compass: FC<CompassProps> = ({
  heading = 0,
  label = 'HEADING',
  size = 180,
  className = '',
}) => {
  const normHeading = ((heading % 360) + 360) % 360;

  return (
    <div
      className={`relative bg-[#0C0E12] border border-[#1A1F2B] rounded-2xl p-4 flex flex-col items-center justify-center select-none ${className}`}
      style={{ width: size, height: size + 30 }}
    >
      <span className="text-[10px] font-mono text-[#5A6475] uppercase tracking-wider mb-2">
        {label}
      </span>

      <div className="relative" style={{ width: size - 40, height: size - 40 }}>
        {/* Outer Dial */}
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="none" stroke="#1A1F2B" strokeWidth="2" />
          <circle cx="50" cy="50" r="42" fill="none" stroke="#242C3A" strokeWidth="1" strokeDasharray="1 3" />

          {/* Fixed Cardinal Labels */}
          <text x="50" y="16" textAnchor="middle" fill="#47F3A0" fontSize="8" fontWeight="bold" fontFamily="Outfit">
            N
          </text>
          <text x="86" y="53" textAnchor="middle" fill="#B0BAC8" fontSize="8" fontFamily="Outfit">
            E
          </text>
          <text x="50" y="90" textAnchor="middle" fill="#B0BAC8" fontSize="8" fontFamily="Outfit">
            S
          </text>
          <text x="14" y="53" textAnchor="middle" fill="#B0BAC8" fontSize="8" fontFamily="Outfit">
            W
          </text>
        </svg>

        {/* Rotating Compass Needle */}
        <div
          className="absolute inset-0 flex items-center justify-center transition-transform duration-500 ease-out"
          style={{ transform: `rotate(${normHeading}deg)` }}
        >
          <div className="w-1.5 h-16 relative flex flex-col items-center">
            {/* North Point (Green) */}
            <div className="w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-b-[24px] border-b-[#47F3A0]" />
            {/* South Point (Muted) */}
            <div className="w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-t-[24px] border-t-[#5A6475]" />
          </div>
        </div>

        {/* Center Pivot */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-3 h-3 rounded-full bg-[#131720] border-2 border-[#47F3A0]" />
        </div>
      </div>

      {/* Digital Readout */}
      <div className="mt-2 font-mono font-bold text-sm text-[#47F3A0]">
        {Math.round(normHeading).toString().padStart(3, '0')}°
      </div>
    </div>
  );
};
