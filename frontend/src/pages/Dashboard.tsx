import type { FC } from 'react';

export const DashboardPage: FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-wide font-['Outfit']">Mission Control Dashboard</h1>
          <p className="text-sm text-[#B0BAC8]">Real-time aerospace telemetry overview for GRU airport sector</p>
        </div>
      </div>
    </div>
  );
};
