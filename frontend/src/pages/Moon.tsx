import type { FC } from 'react';
import { MoonWidget } from '../components/instruments/MoonWidget';
import { DataRow } from '../components/molecules/DataRow';

export const MoonPage: FC = () => {
  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto">
      <h2 className="font-['Outfit'] font-bold text-xl text-white">Lunar Observatory & Ephemeris</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MoonWidget phaseName="Waxing Gibbous" illuminationPct={78.4} ageDays={10.4} className="md:col-span-1 p-6" />

        <div className="md:col-span-2 bg-[#131720] border border-[#1A1F2B] rounded-2xl p-6 flex flex-col justify-between">
          <h3 className="font-['Outfit'] font-bold text-sm text-white border-b border-[#1A1F2B] pb-3 mb-3">
            Lunar Ephemeris Data (GRU Sector)
          </h3>
          <div className="space-y-1">
            <DataRow label="LUNAR PHASE" value="Waxing Gibbous" highlight />
            <DataRow label="ILLUMINATION" value="78.4%" />
            <DataRow label="LUNAR AGE" value="10.4" unit="days" />
            <DataRow label="DISTANCE FROM EARTH" value="384,400" unit="km" />
            <DataRow label="MOONRISE (LOCAL)" value="16:42" />
            <DataRow label="MOONSET (LOCAL)" value="05:18" />
            <DataRow label="NEXT FULL MOON" value="8 days remaining" />
          </div>
        </div>
      </div>
    </div>
  );
};
