import type { FC } from 'react';

export const DiagnosticsPage: FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white font-['Outfit']">System Diagnostics</h1>
      <p className="text-sm text-[#B0BAC8]">Subsystem telemetry, cache metrics, EventBus throughput, and WebSocket logs</p>
    </div>
  );
};
