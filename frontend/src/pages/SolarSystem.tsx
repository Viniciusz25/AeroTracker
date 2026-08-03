import type { FC } from 'react';

interface Planet {
  name: string;
  distanceAu: number;
  magnitude: number;
  constellation: string;
  visibility: string;
}

export const SolarSystemPage: FC = () => {
  const planets: Planet[] = [
    { name: 'Mercury', distanceAu: 0.82, magnitude: -0.4, constellation: 'Leo', visibility: 'Dawn' },
    { name: 'Venus', distanceAu: 0.73, magnitude: -4.2, constellation: 'Virgo', visibility: 'Dusk' },
    { name: 'Mars', distanceAu: 1.45, magnitude: +1.1, constellation: 'Taurus', visibility: 'Midnight' },
    { name: 'Jupiter', distanceAu: 5.12, magnitude: -2.3, constellation: 'Aries', visibility: 'All Night' },
    { name: 'Saturn', distanceAu: 9.85, magnitude: +0.6, constellation: 'Aquarius', visibility: 'All Night' },
    { name: 'Uranus', distanceAu: 19.2, magnitude: +5.7, constellation: 'Taurus', visibility: 'Telescopic' },
    { name: 'Neptune', distanceAu: 29.8, magnitude: +7.8, constellation: 'Pisces', visibility: 'Telescopic' },
  ];

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      <h2 className="font-['Outfit'] font-bold text-xl text-white">Solar System Ephemeris</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {planets.map((planet) => (
          <div
            key={planet.name}
            className="bg-[#131720] border border-[#1A1F2B] hover:border-[#47F3A0]/40 rounded-xl p-4 transition-all"
          >
            <div className="flex items-center justify-between border-b border-[#1A1F2B] pb-2 mb-3">
              <h3 className="font-['Outfit'] font-bold text-base text-white">{planet.name}</h3>
              <span className="text-[10px] font-mono text-[#47F3A0] font-bold">{planet.visibility}</span>
            </div>
            <div className="space-y-1 font-mono text-xs text-[#B0BAC8]">
              <div className="flex justify-between">
                <span>DISTANCE:</span>
                <span className="text-white font-bold">{planet.distanceAu} AU</span>
              </div>
              <div className="flex justify-between">
                <span>MAGNITUDE:</span>
                <span className="text-white font-bold">{planet.magnitude}</span>
              </div>
              <div className="flex justify-between">
                <span>CONSTELLATION:</span>
                <span className="text-[#33A8FF] font-bold">{planet.constellation}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
