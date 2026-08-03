import type { FC } from 'react';
import type { ISSPosition } from '../../types/space.types';

export interface WorldMapProps {
  iss?: ISSPosition | null;
  className?: string;
}

export const WorldMap: FC<WorldMapProps> = ({ iss, className = '' }) => {
  // Equirectangular projection coordinates conversion (360x180 SVG viewport)
  const project = (lat: number, lon: number) => {
    const x = ((lon + 180) / 360) * 360;
    const y = ((90 - lat) / 180) * 180;
    return { x, y };
  };

  const issPos = iss?.position ? project(iss.position.latitude, iss.position.longitude) : null;

  return (
    <div className={`relative bg-[#050608] border border-[#1A1F2B] rounded-2xl overflow-hidden shadow-xl p-2 select-none ${className}`}>
      <svg viewBox="0 0 360 180" className="w-full h-full aspect-[2/1]">
        <defs>
          <radialGradient id="issGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#33A8FF" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#33A8FF" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Latitude/Longitude Grid Lines */}
        {[-60, -30, 0, 30, 60].map((lat) => (
          <line
            key={`lat-${lat}`}
            x1="0"
            y1={((90 - lat) / 180) * 180}
            x2="360"
            y2={((90 - lat) / 180) * 180}
            stroke="#1A1F2B"
            strokeWidth="0.5"
            strokeDasharray="2 2"
          />
        ))}
        {[-120, -60, 0, 60, 120].map((lon) => (
          <line
            key={`lon-${lon}`}
            x1={((lon + 180) / 360) * 360}
            y1="0"
            x2={((lon + 180) / 360) * 360}
            y2="180"
            stroke="#1A1F2B"
            strokeWidth="0.5"
            strokeDasharray="2 2"
          />
        ))}

        {/* Equator & Prime Meridian */}
        <line x1="0" y1="90" x2="360" y2="90" stroke="#00D4FF" strokeOpacity="0.3" strokeWidth="0.8" />
        <line x1="180" y1="0" x2="180" y2="180" stroke="#00D4FF" strokeOpacity="0.3" strokeWidth="0.8" />

        {/* Simplified Continents Outlines */}
        <path
          d="M 50,40 Q 70,30 90,45 T 130,50 T 160,30 T 210,40 T 260,35 T 310,50 T 340,90 T 300,140 T 240,150 T 190,130 T 140,160 T 90,120 T 40,90 Z"
          fill="#131720"
          stroke="#242C3A"
          strokeWidth="1"
        />

        {/* ISS Marker & Orbital Track Footprint */}
        {issPos && (
          <g transform={`translate(${issPos.x}, ${issPos.y})`}>
            {/* Footprint Ring */}
            <circle r="18" fill="url(#issGlow)" opacity="0.3" />
            <circle r="12" fill="none" stroke="#33A8FF" strokeWidth="0.8" opacity="0.6" className="animate-ping" />

            {/* Core Dot */}
            <circle r="3.5" fill="#33A8FF" />
            <circle r="1.5" fill="#FFFFFF" />

            {/* ISS Label */}
            <text x="6" y="-6" fill="#33A8FF" fontSize="7" fontWeight="bold" fontFamily="JetBrains Mono">
              ISS (NORAD 25544)
            </text>
            <text x="6" y="2" fill="#B0BAC8" fontSize="6" fontFamily="JetBrains Mono">
              {iss?.altitude_km?.toFixed(0)}km · {iss?.velocity_kmh?.toLocaleString()}km/h
            </text>
          </g>
        )}
      </svg>
    </div>
  );
};
