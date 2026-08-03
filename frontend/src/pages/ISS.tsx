import type { FC } from 'react';
import { Satellite, Gauge, Eye, Globe } from 'lucide-react';
import { useSpaceData } from '../hooks/useSpaceData';
import { useSpaceStore } from '../store/space.store';
import { WorldMap } from '../components/instruments/WorldMap';
import { MetricCard } from '../components/molecules/MetricCard';
import { DataRow } from '../components/molecules/DataRow';

export const ISSPage: FC = () => {
  useSpaceData();
  const issPosition = useSpaceStore((s) => s.issPosition);

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="ISS Altitude"
          value={issPosition ? Math.round(issPosition.altitude_km) : 420}
          unit="km"
          icon={Satellite}
          variant="primary"
        />
        <MetricCard
          label="Orbital Velocity"
          value={issPosition ? Math.round(issPosition.velocity_kmh).toLocaleString() : '27,576'}
          unit="km/h"
          icon={Gauge}
          variant="secondary"
        />
        <MetricCard
          label="Visual Visibility"
          value={issPosition ? issPosition.visibility.toUpperCase() : 'DAYLIGHT'}
          unit=""
          icon={Eye}
          variant="attention"
        />
        <MetricCard
          label="Ground Footprint"
          value={issPosition ? Math.round(issPosition.footprint_km).toLocaleString() : '4,500'}
          unit="km dia"
          icon={Globe}
          variant="neutral"
        />
      </div>

      {/* World Map Orbit Scope */}
      <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-['Outfit'] font-bold text-lg text-white">ISS Orbital Ground Track Scope</h2>
          <span className="text-xs font-mono text-[#33A8FF] font-semibold">● WHERETHEISS REAL-TIME FEED</span>
        </div>
        <WorldMap iss={issPosition} className="w-full h-[500px]" />
      </div>

      {/* Telemetry Detail Rows */}
      {issPosition && (
        <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-6">
          <h3 className="font-['Outfit'] font-bold text-sm text-white mb-3">Live Telemetry Snapshot</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
            <DataRow label="NORAD CATALOG ID" value={issPosition.norad_id} />
            <DataRow label="GEOGRAPHIC LATITUDE" value={`${issPosition.position.latitude.toFixed(4)}°`} />
            <DataRow label="GEOGRAPHIC LONGITUDE" value={`${issPosition.position.longitude.toFixed(4)}°`} />
            <DataRow label="LAST TIMESTAMP" value={new Date(issPosition.updated_at).toLocaleTimeString()} />
          </div>
        </div>
      )}
    </div>
  );
};
