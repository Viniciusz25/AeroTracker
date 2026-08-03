import type { FC } from 'react';

export const MoonPage: FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white font-['Outfit']">Lunar Observatory</h1>
      <p className="text-sm text-[#B0BAC8]">Moon phase, illumination percentage and rise/set times</p>
    </div>
  );
};
