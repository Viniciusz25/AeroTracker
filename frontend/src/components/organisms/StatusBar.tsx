import { FC, useState, useEffect } from 'react';
import { useSettingsStore } from '../../store/settings.store';
import { useConnectionStore } from '../../store/connection.store';

export const StatusBar: FC = () => {
  const [utcTime, setUtcTime] = useState<string>('');
  const [localTime, setLocalTime] = useState<string>('');
  const { latitude, longitude, radiusKm } = useSettingsStore();
  const channels = useConnectionStore((s) => s.channels);

  useEffect(() => {
    const updateClocks = () => {
      const now = new Date();
      setUtcTime(now.toISOString().substring(11, 19) + ' UTC');
      setLocalTime(now.toLocaleTimeString('pt-BR'));
    };

    updateClocks();
    const interval = setInterval(updateClocks, 1000);
    return () => clearInterval(interval);
  }, []);

  const activeChannelsCount = Object.values(channels).filter(Boolean).length;

  return (
    <footer className="h-8 bg-[#0C0E12] border-t border-[#1A1F2B] px-4 flex items-center justify-between text-[11px] font-mono text-[#5A6475] select-none z-20">
      {/* Coordinates & Range */}
      <div className="flex items-center gap-3">
        <span className="text-[#B0BAC8]">
          POS: <strong className="text-white">{latitude.toFixed(4)}°</strong>,{' '}
          <strong className="text-white">{longitude.toFixed(4)}°</strong>
        </span>
        <span className="text-[#1A1F2B]">|</span>
        <span>
          RAD: <strong className="text-[#47F3A0]">{radiusKm}km</strong>
        </span>
      </div>

      {/* System Status & WS Channels */}
      <div className="hidden sm:flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-[#47F3A0]" />
          <span className="text-[#47F3A0] font-semibold">SYSTEM NOMINAL</span>
        </div>
        <span className="text-[#1A1F2B]">|</span>
        <span>
          WS CHANNELS:{' '}
          <strong className="text-[#33A8FF]">{activeChannelsCount}/4 ACTIVE</strong>
        </span>
      </div>

      {/* Synchronized Clocks */}
      <div className="flex items-center gap-3 font-semibold">
        <span className="text-white">{localTime}</span>
        <span className="text-[#1A1F2B]">|</span>
        <span className="text-[#47F3A0] font-bold">{utcTime}</span>
      </div>
    </footer>
  );
};
