import { FC, useState } from 'react';
import { useAircraftData } from '../hooks/useAircraftData';
import { useAircraftStore } from '../store/aircraft.store';
import { Compass } from '../components/instruments/Compass';
import { Gauge } from '../components/instruments/Gauge';
import { AircraftCard } from '../components/instruments/AircraftCard';

export const FlightsPage: FC = () => {
  useAircraftData();
  const { aircraft } = useAircraftStore();
  const [selectedFlightIcao, setSelectedFlightIcao] = useState<string>(
    aircraft[0]?.icao24 || ''
  );

  const selectedFlight = aircraft.find((a) => a.icao24 === selectedFlightIcao) || aircraft[0];

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header Select Flight */}
      <div className="bg-[#0C0E12] border border-[#1A1F2B] rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="font-['Outfit'] font-bold text-lg text-white">Flight Telemetry & Instrument Panel</h2>
          <p className="text-xs text-[#B0BAC8]">Select a target aircraft to inspect live flight dynamics</p>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs">
          <span className="text-[#5A6475]">ACTIVE TARGET:</span>
          <select
            value={selectedFlightIcao}
            onChange={(e) => setSelectedFlightIcao(e.target.value)}
            className="bg-[#181D25] border border-[#242C3A] rounded-lg px-3 py-1.5 text-white focus:border-[#47F3A0] focus:outline-none"
          >
            {aircraft.map((ac) => (
              <option key={ac.icao24} value={ac.icao24}>
                {ac.callsign || ac.icao24.toUpperCase()} ({ac.on_ground ? 'GND' : 'FLT'})
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedFlight ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Card (1 col) */}
          <div>
            <AircraftCard aircraft={selectedFlight} />
          </div>

          {/* Cockpit Instrument Cluster (2 cols) */}
          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Compass heading={selectedFlight.heading ?? 0} label="HEADING BUS" size={200} className="w-full" />
              <Gauge
                label="INDICATED SPEED"
                value={selectedFlight.velocity?.value ? selectedFlight.velocity.value * 3.6 : 0}
                min={0}
                max={900}
                unit="km/h"
                className="w-full"
              />
              <Gauge
                label="BARO ALTITUDE"
                value={selectedFlight.altitude?.value || 0}
                min={0}
                max={13000}
                unit="m"
                className="w-full"
              />
            </div>

            {/* Simulated Trajectory Map Box */}
            <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-6 relative overflow-hidden h-72 flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-[#47F3A0] font-bold">ROUTE TRAJECTORY LOG</span>
                <span className="text-[#5A6475]">LAT: {selectedFlight.position?.latitude.toFixed(4)}° · LON: {selectedFlight.position?.longitude.toFixed(4)}°</span>
              </div>

              {/* Trajectory Arc Representation */}
              <svg viewBox="0 0 400 120" className="w-full h-32">
                <path d="M 30 100 Q 200 10 370 100" fill="none" stroke="#242C3A" strokeWidth="2" strokeDasharray="4 4" />
                <path d="M 30 100 Q 200 10 240 55" fill="none" stroke="#47F3A0" strokeWidth="3" />
                <circle cx="30" cy="100" r="5" fill="#33A8FF" />
                <text x="20" y="115" fill="#B0BAC8" fontSize="10" fontFamily="JetBrains Mono">SBGR (GRU)</text>
                <circle cx="370" cy="100" r="5" fill="#FFC857" />
                <text x="350" y="115" fill="#B0BAC8" fontSize="10" fontFamily="JetBrains Mono">DEST</text>

                {/* Animated Aircraft on Arc */}
                <g transform="translate(240, 55)">
                  <circle r="6" fill="#47F3A0" className="animate-ping opacity-75" />
                  <circle r="4" fill="#47F3A0" />
                </g>
              </svg>

              <div className="flex justify-between items-center text-xs font-mono text-[#B0BAC8] pt-2 border-t border-[#1A1F2B]">
                <span>SQUAWK: <strong className="text-white">{selectedFlight.squawk || '7000'}</strong></span>
                <span>ORIGIN: <strong className="text-white">{selectedFlight.origin_country}</strong></span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-12 text-center text-[#5A6475] font-mono">
          NO AIRCRAFT SELECTED OR NO ACTIVE RADAR TARGETS AVAILABLE.
        </div>
      )}
    </div>
  );
};
