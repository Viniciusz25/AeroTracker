import type { FC } from 'react';
import { Cloud } from 'lucide-react';
import type { WeatherSnapshot } from '../../types/weather.types';
import { StatusBadge } from '../molecules/StatusBadge';
import { DataRow } from '../molecules/DataRow';

export interface WeatherCardProps {
  weather: WeatherSnapshot | null;
  className?: string;
}

export const WeatherCard: FC<WeatherCardProps> = ({ weather, className = '' }) => {
  if (!weather) {
    return (
      <div className={`bg-[#131720] border border-[#1A1F2B] rounded-2xl p-6 text-center text-[#5A6475] font-mono text-xs ${className}`}>
        LOADING METEOROLOGICAL DATA...
      </div>
    );
  }

  return (
    <div className={`bg-[#131720] border border-[#1A1F2B] rounded-2xl p-5 shadow-2xl backdrop-blur-md ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#1A1F2B] pb-3 mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#33A8FF]/10 border border-[#33A8FF]/30 flex items-center justify-center text-[#33A8FF]">
            <Cloud size={20} />
          </div>
          <div>
            <h3 className="font-['Outfit'] font-bold text-base text-white">{weather.location}</h3>
            <p className="text-xs font-mono text-[#5A6475]">{weather.condition}</p>
          </div>
        </div>
        <StatusBadge status={weather.flight_category === 'IFR' ? 'ifr' : 'vfr'} customLabel={weather.flight_category || 'VFR'} />
      </div>

      {/* Temperature & Feels Like */}
      <div className="flex items-baseline gap-3 mb-4">
        <span className="font-['Outfit'] font-bold text-4xl text-white">
          {weather.temperature_c.toFixed(1)}°C
        </span>
        <span className="text-xs font-mono text-[#B0BAC8]">
          FEELS LIKE <strong className="text-white">{weather.feels_like_c.toFixed(1)}°C</strong>
        </span>
      </div>

      {/* Data Rows */}
      <div className="space-y-1">
        <DataRow label="WIND SPEED" value={weather.wind_speed_ms.toFixed(1)} unit="m/s" />
        <DataRow label="WIND DIRECTION" value={`${weather.wind_direction_deg}°`} />
        <DataRow label="ATMOSPHERIC PRESSURE" value={weather.pressure_hpa} unit="hPa" />
        <DataRow label="RELATIVE HUMIDITY" value={`${weather.humidity_pct}%`} />
        <DataRow label="VISIBILITY" value={(weather.visibility_m / 1000).toFixed(1)} unit="km" />
      </div>

      {/* Raw METAR Bar */}
      {weather.metar && (
        <div className="mt-4 pt-3 border-t border-[#1A1F2B]">
          <span className="text-[9px] font-mono text-[#5A6475] uppercase tracking-wider block mb-1">
            RAW METAR STRING
          </span>
          <div className="bg-[#0C0E12] border border-[#1A1F2B] rounded-lg p-2 font-mono text-[10px] text-[#47F3A0] leading-tight break-all">
            {weather.metar}
          </div>
        </div>
      )}
    </div>
  );
};
