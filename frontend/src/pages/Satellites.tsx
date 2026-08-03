import type { FC } from 'react';

export const SatellitesPage: FC = () => {
  const passes = [
    { name: 'HUBBLE SPACE TELESCOPE', norad: 20580, maxEl: '45°', aos: '19:24:12', los: '19:32:05' },
    { name: 'TIANGONG SPACE STATION', norad: 48274, maxEl: '68°', aos: '20:10:00', los: '20:18:40' },
    { name: 'STARLINK-31042', norad: 54100, maxEl: '82°', aos: '21:05:15', los: '21:11:30' },
    { name: 'NOAA 19 (WEATHER)', norad: 33591, maxEl: '32°', aos: '22:40:00', los: '22:48:10' },
  ];

  return (
    <div className="p-6 space-y-6 max-w-[1500px] mx-auto">
      <h2 className="font-['Outfit'] font-bold text-xl text-white">Upcoming Satellite Passes (GRU Horizon)</h2>

      <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-6">
        <div className="space-y-4">
          {passes.map((pass) => (
            <div key={pass.norad} className="p-4 rounded-xl bg-[#0C0E12] border border-[#1A1F2B] flex flex-wrap items-center justify-between gap-4">
              <div>
                <h3 className="font-['Outfit'] font-bold text-base text-white">{pass.name}</h3>
                <p className="text-xs font-mono text-[#5A6475]">NORAD: {pass.norad}</p>
              </div>
              <div className="flex items-center gap-6 font-mono text-xs">
                <div>MAX ELEVATION: <strong className="text-[#47F3A0]">{pass.maxEl}</strong></div>
                <div>AOS: <strong className="text-white">{pass.aos}</strong></div>
                <div>LOS: <strong className="text-white">{pass.los}</strong></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
