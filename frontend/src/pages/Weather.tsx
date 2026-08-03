import type { FC } from 'react';
import { useWeatherData } from '../hooks/useWeatherData';
import { useWeatherStore } from '../store/weather.store';
import { WeatherCard } from '../components/instruments/WeatherCard';
import { Gauge } from '../components/instruments/Gauge';

export const WeatherPage: FC = () => {
  useWeatherData();
  const currentWeather = useWeatherStore((s) => s.currentWeather);

  return (
    <div className="p-6 space-y-6 max-w-[1500px] mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Weather Card (1 col) */}
        <div>
          <WeatherCard weather={currentWeather} />
        </div>

        {/* Meteorological Instrument Gauges (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="font-['Outfit'] font-bold text-lg text-white">Atmospheric Gauges & Station Sensors</h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Gauge
              label="WIND SPEED"
              value={currentWeather?.wind_speed_ms || 0}
              min={0}
              max={30}
              unit="m/s"
            />
            <Gauge
              label="PRESSURE (QNH)"
              value={currentWeather?.pressure_hpa || 1013}
              min={950}
              max={1050}
              unit="hPa"
            />
            <Gauge
              label="HUMIDITY"
              value={currentWeather?.humidity_pct || 0}
              min={0}
              max={100}
              unit="%"
            />
          </div>

          {/* Meteorological Summary Grid */}
          <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-6 space-y-4">
            <h3 className="font-['Outfit'] font-bold text-sm text-white">Flight Category Rules (ICAO)</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-[#47F3A0]/10 border border-[#47F3A0]/30 text-[#47F3A0]">
                <strong className="block text-sm">VFR</strong>
                <span>Ceiling &gt; 3,000ft</span>
                <span className="block">Vis &gt; 5 miles</span>
              </div>
              <div className="p-3 rounded-xl bg-[#33A8FF]/10 border border-[#33A8FF]/30 text-[#33A8FF]">
                <strong className="block text-sm">MVFR</strong>
                <span>Ceiling 1,000-3,000ft</span>
                <span className="block">Vis 3-5 miles</span>
              </div>
              <div className="p-3 rounded-xl bg-[#FF5D5D]/10 border border-[#FF5D5D]/30 text-[#FF5D5D]">
                <strong className="block text-sm">IFR</strong>
                <span>Ceiling 500-1,000ft</span>
                <span className="block">Vis 1-3 miles</span>
              </div>
              <div className="p-3 rounded-xl bg-[#FF5D5D]/20 border border-[#FF5D5D]/50 text-[#FF5D5D]">
                <strong className="block text-sm">LIFR</strong>
                <span>Ceiling &lt; 500ft</span>
                <span className="block">Vis &lt; 1 mile</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
