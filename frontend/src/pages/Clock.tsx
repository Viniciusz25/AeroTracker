import type { FC } from 'react';

export const ClockPage: FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white font-['Outfit']">Master Aerospace Clock</h1>
      <p className="text-sm text-[#B0BAC8]">UTC, Sidereal, Zulu and local airport clocks</p>
    </div>
  );
};
