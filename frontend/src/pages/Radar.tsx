import type { FC } from 'react';

export const RadarPage: FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white font-['Outfit']">Air Traffic Radar</h1>
      <p className="text-sm text-[#B0BAC8]">10km Radius ADS-B Live Tracking centered at GRU</p>
    </div>
  );
};
