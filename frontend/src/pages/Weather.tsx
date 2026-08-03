import type { FC } from 'react';

export const WeatherPage: FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white font-['Outfit']">Aviation Weather</h1>
      <p className="text-sm text-[#B0BAC8]">METAR, TAF and local meteorological radar data</p>
    </div>
  );
};
