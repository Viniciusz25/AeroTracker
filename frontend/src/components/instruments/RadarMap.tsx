import { FC, useState } from 'react';
import { Plane } from 'lucide-react';
import type { AircraftState } from '../../types/aircraft.types';
import { useSettingsStore } from '../../store/settings.store';
import { useAircraftStore } from '../../store/aircraft.store';

export interface RadarMapProps {
  aircraft?: AircraftState[];
  onSelectAircraft?: (icao24: string) => void;
  className?: string;
}

export const RadarMap: FC<RadarMapProps> = ({
  aircraft = [],
  onSelectAircraft,
  className = '',
}) => {
  const { latitude: centerLat, longitude: centerLon } = useSettingsStore();
  const { selectedIcao, selectAircraft, radarRangeKm } = useAircraftStore();
  const [hoveredAircraft, setHoveredAircraft] = useState<AircraftState | null>(null);

  // Map latitude/longitude offsets to percentage coordinates on 500x500 viewport
  const centerPx = 250;
  // 1 degree latitude ≈ 111km. Range in km is radius of the circle
  const kmPerDegree = 111.0;
  const scale = (centerPx / (radarRangeKm / kmPerDegree));

  const project = (lat: number, lon: number) => {
    const dLat = lat - centerLat;
    const dLon = (lon - centerLon) * Math.cos((centerLat * Math.PI) / 180);
    const x = centerPx + dLon * scale;
    const y = centerPx - dLat * scale; // Invert Y axis for screen
    return { x, y };
  };

  return (
    <div className={`relative bg-[#020A06] border border-[#1A1F2B] rounded-2xl overflow-hidden shadow-2xl flex items-center justify-center select-none ${className}`}>
      <svg viewBox="0 0 500 500" className="w-full h-full max-w-[600px] aspect-square">
        <defs>
          {/* Radar background grid pattern */}
          <radialGradient id="radarBg" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#041F14" stopOpacity="0.8" />
            <stop offset="70%" stopColor="#020E08" stopOpacity="0.95" />
            <stop offset="100%" stopColor="#010604" stopOpacity="1" />
          </radialGradient>

          {/* Radar sweep gradient */}
          <linearGradient id="sweepGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#47F3A0" stopOpacity="0.4" />
            <stop offset="50%" stopColor="#47F3A0" stopOpacity="0.1" />
            <stop offset="100%" stopColor="#47F3A0" stopOpacity="0" />
          </linearGradient>

          {/* Glow filter for aircraft blips */}
          <filter id="blipGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Background scope */}
        <circle cx={centerPx} cy={centerPx} r={centerPx - 5} fill="url(#radarBg)" stroke="#1A1F2B" strokeWidth="2" />

        {/* Concentric Range Rings (2.5km, 5km, 7.5km, 10km) */}
        {[0.25, 0.5, 0.75, 0.95].map((ratio, i) => (
          <circle
            key={i}
            cx={centerPx}
            cy={centerPx}
            r={(centerPx - 10) * ratio}
            fill="none"
            stroke="#00D4FF"
            strokeOpacity={0.12}
            strokeDasharray={i % 2 === 1 ? '4 4' : undefined}
            strokeWidth="1"
          />
        ))}

        {/* Distance Range Labels */}
        {[0.25, 0.5, 0.75, 0.95].map((ratio, i) => (
          <text
            key={`lbl-${i}`}
            x={centerPx + 6}
            y={centerPx - (centerPx - 10) * ratio + 12}
            fill="#00D4FF"
            fillOpacity={0.4}
            fontSize="9"
            fontFamily="JetBrains Mono"
          >
            {(radarRangeKm * ratio).toFixed(1)}km
          </text>
        ))}

        {/* Crosshair & Degree lines */}
        <line x1={centerPx} y1={10} x2={centerPx} y2={490} stroke="#00D4FF" strokeOpacity={0.15} strokeWidth="1" />
        <line x1={10} y1={centerPx} x2={490} y2={centerPx} stroke="#00D4FF" strokeOpacity={0.15} strokeWidth="1" />
        <line x1={80} y1={80} x2={420} y2={420} stroke="#00D4FF" strokeOpacity={0.08} strokeWidth="1" strokeDasharray="3 3" />
        <line x1={420} y1={80} x2={80} y2={420} stroke="#00D4FF" strokeOpacity={0.08} strokeWidth="1" strokeDasharray="3 3" />

        {/* Cardinal Markers */}
        <text x={centerPx} y={24} textAnchor="middle" fill="#47F3A0" fontSize="12" fontWeight="bold" fontFamily="Outfit">N (000°)</text>
        <text x={480} y={centerPx + 4} textAnchor="end" fill="#B0BAC8" fontSize="11" fontFamily="Outfit">E (090°)</text>
        <text x={centerPx} y={486} textAnchor="middle" fill="#B0BAC8" fontSize="11" fontFamily="Outfit">S (180°)</text>
        <text x={20} y={centerPx + 4} textAnchor="start" fill="#B0BAC8" fontSize="11" fontFamily="Outfit">W (270°)</text>

        {/* Center Station Marker (GRU) */}
        <g transform={`translate(${centerPx}, ${centerPx})`}>
          <circle r="4" fill="#47F3A0" filter="url(#blipGlow)" />
          <circle r="8" fill="none" stroke="#47F3A0" strokeWidth="1" opacity="0.6" className="animate-ping" />
        </g>

        {/* Rotating 360° Sweep Line */}
        <g transform={`translate(${centerPx}, ${centerPx})`}>
          <g className="animate-radar-sweep">
            <line x1="0" y1="0" x2="0" y2={-(centerPx - 10)} stroke="#47F3A0" strokeWidth="2" opacity="0.8" />
            <polygon points={`0,0 20,-${centerPx - 10} -20,-${centerPx - 10}`} fill="url(#sweepGradient)" />
          </g>
        </g>

        {/* Aircraft Blips */}
        {aircraft.map((ac) => {
          if (!ac.position) return null;
          const { x, y } = project(ac.position.latitude, ac.position.longitude);

          // Skip if out of circular scope bounds
          const distFromCenter = Math.hypot(x - centerPx, y - centerPx);
          if (distFromCenter > centerPx - 15) return null;

          const isSelected = selectedIcao === ac.icao24;
          const isHovered = hoveredAircraft?.icao24 === ac.icao24;
          const heading = ac.heading ?? 0;

          return (
            <g
              key={ac.icao24}
              transform={`translate(${x}, ${y})`}
              className="cursor-pointer transition-transform duration-300 hover:scale-125"
              onClick={() => {
                selectAircraft(ac.icao24);
                if (onSelectAircraft) onSelectAircraft(ac.icao24);
              }}
              onMouseEnter={() => setHoveredAircraft(ac)}
              onMouseLeave={() => setHoveredAircraft(null)}
            >
              {/* Target Highlight Ring if Selected */}
              {isSelected && (
                <circle r="16" fill="none" stroke="#47F3A0" strokeWidth="1.5" strokeDasharray="3 3" className="animate-spin" />
              )}

              {/* Directional Aircraft Icon */}
              <g transform={`rotate(${heading})`}>
                <Plane
                  size={16}
                  x={-8}
                  y={-8}
                  className={
                    ac.on_ground
                      ? 'text-[#FFC857]'
                      : isSelected
                      ? 'text-[#47F3A0] filter drop-shadow-[0_0_8px_#47F3A0]'
                      : 'text-[#00D4FF]'
                  }
                />
              </g>

              {/* Data Tag Overlay on Hover/Select */}
              {(isSelected || isHovered) && (
                <g transform="translate(12, -12)">
                  <rect x="0" y="0" width="70" height="28" rx="4" fill="#0C0E12" fillOpacity="0.9" stroke="#47F3A0" strokeWidth="1" />
                  <text x="5" y="11" fill="#FFFFFF" fontSize="9" fontWeight="bold" fontFamily="JetBrains Mono">
                    {ac.callsign || ac.icao24.toUpperCase()}
                  </text>
                  <text x="5" y="22" fill="#47F3A0" fontSize="8" fontFamily="JetBrains Mono">
                    {ac.altitude?.value ? `${Math.round(ac.altitude.value)}m` : 'GND'} · {ac.velocity?.value ? `${Math.round(ac.velocity.value * 3.6)}kmh` : '0'}
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </svg>

      {/* Scope Footer Overlay */}
      <div className="absolute bottom-3 left-4 right-4 flex items-center justify-between text-[10px] font-mono text-[#B0BAC8] bg-[#0C0E12]/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-[#1A1F2B]">
        <div>TARGETS: <strong className="text-[#47F3A0]">{aircraft.length}</strong></div>
        <div>CENTER: <strong className="text-white">SBGR / GRU</strong></div>
        <div>RANGE: <strong className="text-[#00D4FF]">{radarRangeKm} KM</strong></div>
      </div>
    </div>
  );
};
