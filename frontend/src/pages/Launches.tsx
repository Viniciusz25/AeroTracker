import type { FC } from 'react';
import { useSpaceData } from '../hooks/useSpaceData';
import { useSpaceStore } from '../store/space.store';
import { LaunchCard } from '../components/instruments/LaunchCard';

export const LaunchesPage: FC = () => {
  useSpaceData();
  const launches = useSpaceStore((s) => s.launches);

  const fallbackLaunches = [
    {
      id: 'starlink-g10',
      name: 'Starlink Group 10-23',
      vehicle: 'Falcon 9 Block 5',
      provider: 'SpaceX',
      pad: 'SLC-40, Cape Canaveral',
      status: 'Go',
      net: new Date(Date.now() + 86400000).toISOString(),
      probability_pct: 95,
      mission_type: 'Communications',
    },
    {
      id: 'artemis-ii',
      name: 'Artemis II Crewed Test',
      vehicle: 'SLS Block 1',
      provider: 'NASA',
      pad: 'LC-39B, Kennedy Space Center',
      status: 'Go',
      net: new Date(Date.now() + 86400000 * 120).toISOString(),
      probability_pct: 90,
      mission_type: 'Lunar Orbit',
    },
  ];

  const activeLaunches = launches.length > 0 ? launches : fallbackLaunches;

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      <h2 className="font-['Outfit'] font-bold text-xl text-white">Global Space Launch Manifest</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {activeLaunches.map((launch) => (
          <LaunchCard key={launch.id} launch={launch} />
        ))}
      </div>
    </div>
  );
};
