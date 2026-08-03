import type { FC } from 'react';
import { ClockWidget } from '../components/instruments/ClockWidget';

export const ClockPage: FC = () => {
  return (
    <div className="p-6 space-y-6 max-w-[1500px] mx-auto">
      <h2 className="font-['Outfit'] font-bold text-xl text-white">Master Aerospace Clocks</h2>

      {/* Main UTC Primary Chrono */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ClockWidget label="UTC MASTER ZULU CHRONO" timezone="UTC" className="p-8" />
        <ClockWidget label="LOCAL STATION TIME (SBGR)" timezone="America/Sao_Paulo" className="p-8" />
      </div>

      {/* World Airport Clocks Grid */}
      <h3 className="font-['Outfit'] font-semibold text-base text-white pt-4">Global Aviation Hub Clocks</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ClockWidget label="LONDON (EGLL / LHR)" timezone="Europe/London" />
        <ClockWidget label="NEW YORK (KJFK / JFK)" timezone="America/New_York" />
        <ClockWidget label="TOKYO (RJTT / HND)" timezone="Asia/Tokyo" />
      </div>
    </div>
  );
};
