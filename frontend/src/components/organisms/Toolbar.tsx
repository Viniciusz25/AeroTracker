import type { FC } from 'react';
import { useLocation } from 'react-router-dom';
import { MapPin, Wifi, RefreshCw } from 'lucide-react';
import { useSettingsStore } from '../../store/settings.store';
import { useConnectionStore } from '../../store/connection.store';

export const Toolbar: FC = () => {
  const location = useLocation();
  const { locationName, radiusKm } = useSettingsStore();
  const isAircraftConnected = useConnectionStore((s) => s.isConnected('aircraft'));

  const getPageInfo = (path: string) => {
    switch (path) {
      case '/radar':
        return { title: 'Air Traffic Radar', subtitle: 'Live ADS-B tracking within sector' };
      case '/flights':
        return { title: 'Flight Telemetry', subtitle: 'Flight trajectory & cockpit data' };
      case '/weather':
        return { title: 'Aviation Weather', subtitle: 'METAR & atmospheric conditions' };
      case '/clock':
        return { title: 'Master Clock', subtitle: 'UTC, Zulu & airport timing' };
      case '/iss':
        return { title: 'ISS Observatory', subtitle: 'Real-time space station telemetry' };
      case '/moon':
        return { title: 'Lunar Tracker', subtitle: 'Phase, illumination & ephemeris' };
      case '/solar-system':
        return { title: 'Solar Ephemeris', subtitle: 'Planetary positions & distances' };
      case '/satellites':
        return { title: 'Satellite Passes', subtitle: 'LEO/GEO ground tracks & horizons' };
      case '/launches':
        return { title: 'Space Launches', subtitle: 'Global launch schedules & countdowns' };
      case '/settings':
        return { title: 'System Settings', subtitle: 'Station preferences & API keys' };
      case '/diagnostics':
        return { title: 'System Diagnostics', subtitle: 'Subsystem metrics & EventBus logs' };
      default:
        return { title: 'Mission Control', subtitle: 'Real-time aerospace telemetry dashboard' };
    }
  };

  const info = getPageInfo(location.pathname);

  return (
    <header className="h-16 bg-[#0C0E12]/80 border-b border-[#1A1F2B] backdrop-blur-md px-6 flex items-center justify-between z-20">
      {/* Title & Subtitle */}
      <div>
        <h2 className="font-['Outfit'] font-bold text-lg text-white tracking-wide">
          {info.title}
        </h2>
        <p className="text-xs text-[#B0BAC8] font-['Inter']">{info.subtitle}</p>
      </div>

      {/* Station Indicators */}
      <div className="flex items-center gap-4 text-xs font-mono">
        {/* Location badge */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#181D25] border border-[#242C3A] text-[#B0BAC8]">
          <MapPin size={14} className="text-[#47F3A0]" />
          <span>{locationName}</span>
          <span className="text-[#47F3A0] font-bold">({radiusKm}km)</span>
        </div>

        {/* WebSocket / API Connection Status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#181D25] border border-[#242C3A]">
          <Wifi
            size={14}
            className={isAircraftConnected ? 'text-[#47F3A0]' : 'text-[#5A6475]'}
          />
          <span className={isAircraftConnected ? 'text-[#47F3A0]' : 'text-[#5A6475]'}>
            {isAircraftConnected ? 'STREAM LIVE' : 'REST ACTIVE'}
          </span>
        </div>

        {/* Refresh indicator */}
        <button
          onClick={() => window.location.reload()}
          className="p-2 rounded-lg bg-[#181D25] border border-[#242C3A] text-[#5A6475] hover:text-white hover:border-[#47F3A0]/50 transition-colors cursor-pointer"
          title="Force refresh data"
        >
          <RefreshCw size={14} />
        </button>
      </div>
    </header>
  );
};
