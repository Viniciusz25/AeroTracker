import type { FC } from 'react';
import { Plane, Compass, ArrowUpRight } from 'lucide-react';
import type { AircraftState } from '../../types/aircraft.types';
import { StatusBadge } from '../molecules/StatusBadge';
import { DataRow } from '../molecules/DataRow';

export interface AircraftCardProps {
  aircraft: AircraftState;
  onClose?: () => void;
  className?: string;
}

export const AircraftCard: FC<AircraftCardProps> = ({ aircraft, className = '' }) => {
  const altMeters = aircraft.altitude?.value;
  const speedKmh = aircraft.velocity?.value ? aircraft.velocity.value * 3.6 : null;

  return (
    <div className={`bg-[#131720] border border-[#1A1F2B] rounded-2xl p-5 shadow-2xl backdrop-blur-md font-['Inter'] ${className}`}>
      {/* Header with Callsign & Status */}
      <div className="flex items-center justify-between border-b border-[#1A1F2B] pb-3 mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#47F3A0]/10 border border-[#47F3A0]/30 flex items-center justify-center text-[#47F3A0]">
            <Plane size={20} className="transform -rotate-45" />
          </div>
          <div>
            <h3 className="font-['Outfit'] font-bold text-lg text-white tracking-wide">
              {aircraft.callsign || aircraft.icao24.toUpperCase()}
            </h3>
            <p className="text-xs font-mono text-[#5A6475]">ICAO24: {aircraft.icao24.toUpperCase()}</p>
          </div>
        </div>
        <StatusBadge status={aircraft.on_ground ? 'ground' : 'airborne'} />
      </div>

      {/* Telemetry Data Grid */}
      <div className="space-y-1">
        <DataRow
          label="BARO ALTITUDE"
          value={altMeters !== undefined && altMeters !== null ? Math.round(altMeters).toLocaleString() : 'GND'}
          unit={altMeters !== undefined && altMeters !== null ? 'm' : ''}
          highlight={!aircraft.on_ground}
        />
        <DataRow
          label="GROUND SPEED"
          value={speedKmh !== null ? Math.round(speedKmh).toString() : '0'}
          unit="km/h"
        />
        <DataRow
          label="HEADING"
          value={aircraft.heading !== null ? `${Math.round(aircraft.heading)}°` : 'N/A'}
        />
        <DataRow
          label="VERTICAL RATE"
          value={aircraft.vertical_rate !== null ? `${aircraft.vertical_rate.toFixed(1)} m/s` : '0 m/s'}
        />
        <DataRow
          label="ORIGIN COUNTRY"
          value={aircraft.origin_country || 'Unknown'}
        />
        <DataRow
          label="TRANSPONDER SQUAWK"
          value={aircraft.squawk || '7000'}
        />
        <DataRow
          label="SENSOR SOURCE"
          value={aircraft.position_source || 'ADS-B'}
        />
      </div>

      {/* Primary Telemetry Pills */}
      <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-[#1A1F2B]">
        <div className="bg-[#0C0E12] border border-[#1A1F2B] rounded-lg p-2.5 flex items-center gap-2">
          <Compass size={16} className="text-[#33A8FF]" />
          <div className="flex flex-col">
            <span className="text-[9px] font-mono text-[#5A6475]">HEADING</span>
            <span className="text-xs font-mono font-bold text-white">
              {aircraft.heading !== null ? `${Math.round(aircraft.heading)}°` : '000°'}
            </span>
          </div>
        </div>

        <div className="bg-[#0C0E12] border border-[#1A1F2B] rounded-lg p-2.5 flex items-center gap-2">
          <ArrowUpRight size={16} className="text-[#47F3A0]" />
          <div className="flex flex-col">
            <span className="text-[9px] font-mono text-[#5A6475]">CATEGORY</span>
            <span className="text-xs font-mono font-bold text-[#47F3A0] uppercase truncate">
              {aircraft.category || 'COMMERCIAL'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
