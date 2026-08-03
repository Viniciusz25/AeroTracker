import type { FC } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchStatus, fetchModules } from '../services/system.service';
import { StatusBadge } from '../components/molecules/StatusBadge';

export const DiagnosticsPage: FC = () => {
  const { data: statusData } = useQuery({
    queryKey: ['system-status'],
    queryFn: fetchStatus,
    refetchInterval: 3000,
  });

  const { data: modulesData } = useQuery({
    queryKey: ['system-modules'],
    queryFn: fetchModules,
    refetchInterval: 3000,
  });

  return (
    <div className="p-6 space-y-6 max-w-[1500px] mx-auto">
      <h2 className="font-['Outfit'] font-bold text-xl text-white">System Diagnostics & Module Status</h2>

      {/* Subsystem Telemetry */}
      {statusData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-5 font-mono text-xs space-y-2">
            <span className="text-[#5A6475] uppercase block font-bold mb-2">SYSTEM UPTIME</span>
            <div className="text-2xl font-['Outfit'] font-bold text-[#47F3A0]">
              {statusData.uptime_seconds}s
            </div>
            <div>VERSION: <strong className="text-white">{statusData.version}</strong></div>
          </div>

          <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-5 font-mono text-xs space-y-2">
            <span className="text-[#5A6475] uppercase block font-bold mb-2">WEBSOCKET POOL</span>
            <div className="text-2xl font-['Outfit'] font-bold text-[#33A8FF]">
              {statusData.websocket.total_connections} active
            </div>
            <div>CHANNELS: <strong className="text-white">{Object.keys(statusData.websocket.channels).length} open</strong></div>
          </div>

          <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-5 font-mono text-xs space-y-2">
            <span className="text-[#5A6475] uppercase block font-bold mb-2">SECTOR LOCATION</span>
            <div className="text-sm font-['Outfit'] font-bold text-white">
              {statusData.location.name}
            </div>
            <div>LAT/LON: <strong className="text-[#47F3A0]">{statusData.location.latitude}, {statusData.location.longitude}</strong></div>
          </div>
        </div>
      )}

      {/* Modules Health Catalog Table */}
      {modulesData && (
        <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-6">
          <h3 className="font-['Outfit'] font-bold text-base text-white mb-4">Module Catalog & Scheduler Jobs</h3>
          <div className="space-y-2">
            {modulesData.modules.map((mod) => (
              <div
                key={mod.name}
                className="p-3 rounded-xl bg-[#0C0E12] border border-[#1A1F2B] flex flex-wrap items-center justify-between gap-4 font-mono text-xs"
              >
                <div>
                  <div className="font-['Outfit'] font-bold text-sm text-white">{mod.display_name}</div>
                  <div className="text-[10px] text-[#5A6475]">{mod.description}</div>
                </div>

                <div className="flex items-center gap-6">
                  <div>INTERVAL: <strong className="text-white">{mod.interval_seconds}s</strong></div>
                  <StatusBadge status={mod.active ? 'online' : 'offline'} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
