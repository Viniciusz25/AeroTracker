import { FC, useState, useEffect } from 'react';
import { Rocket } from 'lucide-react';
import type { LaunchItem } from '../../types/space.types';
import { StatusBadge } from '../molecules/StatusBadge';

export interface LaunchCardProps {
  launch: LaunchItem;
  className?: string;
}

export const LaunchCard: FC<LaunchCardProps> = ({ launch, className = '' }) => {
  const [countdown, setCountdown] = useState<string>('T-00:00:00');

  useEffect(() => {
    const updateCountdown = () => {
      const target = new Date(launch.net).getTime();
      const now = new Date().getTime();
      const diff = target - now;

      if (diff <= 0) {
        setCountdown('LAUNCHED / IN FLIGHT');
        return;
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      const hh = hours.toString().padStart(2, '0');
      const mm = minutes.toString().padStart(2, '0');
      const ss = seconds.toString().padStart(2, '0');

      setCountdown(`T-${hh}:${mm}:${ss}`);
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
    return () => clearInterval(interval);
  }, [launch.net]);

  return (
    <div className={`bg-[#131720] border border-[#1A1F2B] rounded-2xl p-5 shadow-xl backdrop-blur-md flex flex-col justify-between ${className}`}>
      <div>
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#1A1F2B] pb-3 mb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-[#FF5D5D]/10 border border-[#FF5D5D]/30 flex items-center justify-center text-[#FF5D5D]">
              <Rocket size={18} />
            </div>
            <div>
              <span className="text-[10px] font-mono text-[#5A6475] uppercase">{launch.provider}</span>
              <h3 className="font-['Outfit'] font-bold text-base text-white tracking-wide">{launch.name}</h3>
            </div>
          </div>
          <StatusBadge status={launch.status === 'Go' ? 'online' : 'warning'} customLabel={launch.status || 'GO'} />
        </div>

        {/* Mission details */}
        <div className="space-y-2 text-xs font-mono">
          <div className="flex items-center justify-between">
            <span className="text-[#5A6475]">VEHICLE:</span>
            <span className="text-white font-semibold">{launch.vehicle}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[#5A6475]">LOCATION:</span>
            <span className="text-[#B0BAC8] truncate max-w-[180px]">{launch.pad}</span>
          </div>
          {launch.probability_pct && (
            <div className="flex items-center justify-between">
              <span className="text-[#5A6475]">WEATHER GO:</span>
              <span className="text-[#47F3A0] font-bold">{launch.probability_pct}%</span>
            </div>
          )}
        </div>
      </div>

      {/* Countdown Timer Bar */}
      <div className="mt-4 pt-3 border-t border-[#1A1F2B] bg-[#0C0E12] p-2.5 rounded-xl border border-[#1A1F2B] flex items-center justify-between">
        <span className="text-[10px] font-mono text-[#5A6475] font-semibold">COUNTDOWN</span>
        <span className="font-['Outfit'] font-bold text-base text-[#47F3A0] font-mono tracking-wider">
          {countdown}
        </span>
      </div>
    </div>
  );
};
