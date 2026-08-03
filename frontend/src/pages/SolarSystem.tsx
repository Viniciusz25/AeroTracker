import type { FC } from 'react';

export const SolarSystemPage: FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white font-['Outfit']">Solar System Ephemeris</h1>
      <p className="text-sm text-[#B0BAC8]">Planetary positions, elongation, and distances from Earth</p>
    </div>
  );
};
