import type { FC } from 'react';
import { Plane, Cloud, Satellite, Rocket } from 'lucide-react';
import { useAircraftData } from '../hooks/useAircraftData';
import { useWeatherData } from '../hooks/useWeatherData';
import { useSpaceData } from '../hooks/useSpaceData';

import { useAircraftStore } from '../store/aircraft.store';
import { useWeatherStore } from '../store/weather.store';
import { useSpaceStore } from '../store/space.store';

import { MetricCard } from '../components/molecules/MetricCard';
import { RadarMap } from '../components/instruments/RadarMap';
import { WeatherCard } from '../components/instruments/WeatherCard';
import { WorldMap } from '../components/instruments/WorldMap';
import { ClockWidget } from '../components/instruments/ClockWidget';
import { LaunchCard } from '../components/instruments/LaunchCard';

export const DashboardPage: FC = () => {
  useAircraftData();
  useWeatherData();
  useSpaceData();

  const { aircraft, airborneCount, totalCount } = useAircraftStore();
  const currentWeather = useWeatherStore((s) => s.currentWeather);
  const { issPosition, launches } = useSpaceStore();

  const nextLaunch = launches[0] || {
    id: 'starlink-g10',
    name: 'Starlink Group 10-23',
    vehicle: 'Falcon 9 Block 5',
    provider: 'SpaceX',
    pad: 'SLC-40, Cape Canaveral',
    status: 'Go',
    net: new Date(Date.now() + 86400000).toISOString(),
    probability_pct: 95,
    mission_type: 'Communications',
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Top 4 KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Airborne Targets"
          value={airborneCount}
          unit={`/ ${totalCount} total`}
          icon={Plane}
          variant="primary"
        />
        <MetricCard
          label="Local Temperature"
          value={currentWeather ? `${currentWeather.temperature_c.toFixed(1)}°C` : '--'}
          unit={currentWeather?.flight_category || 'VFR'}
          icon={Cloud}
          variant="secondary"
        />
        <MetricCard
          label="ISS Altitude"
          value={issPosition ? `${Math.round(issPosition.altitude_km)}` : '420'}
          unit="km"
          icon={Satellite}
          variant="attention"
        />
        <MetricCard
          label="Next Space Launch"
          value={launches.length > 0 ? launches.length : '1'}
          unit="scheduled"
          icon={Rocket}
          variant="danger"
        />
      </div>

      {/* Main Aerospace Monitoring Split: Radar Scope + Weather & Clocks */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Radar Scope (2 cols) */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          <div className="flex items-center justify-between px-1">
            <h2 className="font-['Outfit'] font-bold text-lg text-white">Live Sector Radar Scope</h2>
            <span className="text-xs font-mono text-[#47F3A0]">● REAL-TIME OPENSKY TELEMETRY</span>
          </div>
          <RadarMap aircraft={aircraft} className="w-full h-[520px]" />
        </div>

        {/* Side Instruments (1 col): Weather + Clock + ISS */}
        <div className="flex flex-col gap-4">
          <ClockWidget label="UTC MASTER CHRONO" timezone="UTC" />
          <WeatherCard weather={currentWeather} />
          <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-4">
            <div className="text-xs font-mono text-[#5A6475] uppercase mb-2">ISS Orbital Ground Track</div>
            <WorldMap iss={issPosition} className="h-44" />
          </div>
        </div>
      </div>

      {/* Launch Schedule Section */}
      <div className="space-y-3">
        <h2 className="font-['Outfit'] font-bold text-lg text-white">Featured Launch Manifest</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <LaunchCard launch={nextLaunch} />
        </div>
      </div>
    </div>
  );
};
