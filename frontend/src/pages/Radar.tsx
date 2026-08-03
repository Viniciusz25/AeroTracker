import { FC, useState } from 'react';
import { Search } from 'lucide-react';
import { useAircraftData } from '../hooks/useAircraftData';
import { useAircraftStore } from '../store/aircraft.store';
import { RadarMap } from '../components/instruments/RadarMap';
import { AircraftCard } from '../components/instruments/AircraftCard';
import { StatusBadge } from '../components/molecules/StatusBadge';

export const RadarPage: FC = () => {
  useAircraftData();
  const { aircraft, selectedAircraft, selectAircraft, totalCount, airborneCount, onGroundCount } =
    useAircraftStore();

  const [filter, setFilter] = useState<'all' | 'airborne' | 'ground'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredAircraft = aircraft.filter((ac) => {
    if (filter === 'airborne' && ac.on_ground) return false;
    if (filter === 'ground' && !ac.on_ground) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      const callsign = (ac.callsign || '').toLowerCase();
      const icao = ac.icao24.toLowerCase();
      return callsign.includes(term) || icao.includes(term);
    }
    return true;
  });

  return (
    <div className="p-6 h-full flex flex-col gap-4 max-w-[1700px] mx-auto">
      {/* Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-[#0C0E12] border border-[#1A1F2B] rounded-xl p-3">
        {/* Filter buttons */}
        <div className="flex items-center gap-2 font-mono text-xs">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg border transition-all cursor-pointer ${
              filter === 'all'
                ? 'bg-[#47F3A0]/10 text-[#47F3A0] border-[#47F3A0]/40 font-bold'
                : 'bg-[#181D25] text-[#B0BAC8] border-[#242C3A]'
            }`}
          >
            ALL ({totalCount})
          </button>
          <button
            onClick={() => setFilter('airborne')}
            className={`px-3 py-1.5 rounded-lg border transition-all cursor-pointer ${
              filter === 'airborne'
                ? 'bg-[#47F3A0]/10 text-[#47F3A0] border-[#47F3A0]/40 font-bold'
                : 'bg-[#181D25] text-[#B0BAC8] border-[#242C3A]'
            }`}
          >
            AIRBORNE ({airborneCount})
          </button>
          <button
            onClick={() => setFilter('ground')}
            className={`px-3 py-1.5 rounded-lg border transition-all cursor-pointer ${
              filter === 'ground'
                ? 'bg-[#FFC857]/10 text-[#FFC857] border-[#FFC857]/40 font-bold'
                : 'bg-[#181D25] text-[#B0BAC8] border-[#242C3A]'
            }`}
          >
            ON GROUND ({onGroundCount})
          </button>
        </div>

        {/* Search input */}
        <div className="relative w-64">
          <Search size={14} className="absolute left-3 top-2.5 text-[#5A6475]" />
          <input
            type="text"
            placeholder="Search Callsign / ICAO..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#181D25] border border-[#242C3A] rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-[#5A6475] focus:border-[#47F3A0] focus:outline-none font-mono"
          />
        </div>
      </div>

      {/* Main Radar Layout: Scope (Left 65%) + Target List / Detail (Right 35%) */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[600px]">
        {/* Radar Scope (8 cols) */}
        <div className="lg:col-span-8 flex flex-col">
          <RadarMap aircraft={filteredAircraft} className="w-full h-full min-h-[550px]" />
        </div>

        {/* Right Panel: Target List / Target Detail Card (4 cols) */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          {selectedAircraft ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-[#47F3A0] font-bold">TARGET TELEMETRY LOCK</span>
                <button
                  onClick={() => selectAircraft(null)}
                  className="text-xs font-mono text-[#5A6475] hover:text-white underline cursor-pointer"
                >
                  Close Detail
                </button>
              </div>
              <AircraftCard aircraft={selectedAircraft} />
            </div>
          ) : (
            <div className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-4 flex-1 flex flex-col overflow-hidden">
              <h3 className="font-['Outfit'] font-bold text-sm text-white mb-3 flex items-center justify-between">
                <span>Detected Targets</span>
                <span className="text-xs font-mono text-[#47F3A0]">{filteredAircraft.length} targets</span>
              </h3>

              <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                {filteredAircraft.map((ac) => (
                  <div
                    key={ac.icao24}
                    onClick={() => selectAircraft(ac.icao24)}
                    className="p-3 rounded-xl bg-[#0C0E12] border border-[#1A1F2B] hover:border-[#47F3A0]/40 transition-all cursor-pointer flex items-center justify-between"
                  >
                    <div>
                      <div className="font-['Outfit'] font-bold text-sm text-white">
                        {ac.callsign || ac.icao24.toUpperCase()}
                      </div>
                      <div className="text-[11px] font-mono text-[#5A6475]">
                        {ac.altitude?.value ? `${Math.round(ac.altitude.value)}m` : 'GND'} ·{' '}
                        {ac.velocity?.value ? `${Math.round(ac.velocity.value * 3.6)}kmh` : '0'}
                      </div>
                    </div>
                    <StatusBadge status={ac.on_ground ? 'ground' : 'airborne'} />
                  </div>
                ))}
                {filteredAircraft.length === 0 && (
                  <div className="text-center py-12 text-xs font-mono text-[#5A6475]">
                    No targets detected in current range/filter.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
