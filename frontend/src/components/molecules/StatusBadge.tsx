import type { FC } from 'react';

export interface StatusBadgeProps {
  status: 'online' | 'offline' | 'warning' | 'error' | 'airborne' | 'ground' | 'vfr' | 'ifr';
  customLabel?: string;
  className?: string;
}

export const StatusBadge: FC<StatusBadgeProps> = ({ status, customLabel, className = '' }) => {
  const config = {
    online: { label: 'ONLINE', bg: 'bg-[#47F3A0]/10', text: 'text-[#47F3A0]', border: 'border-[#47F3A0]/30', dot: 'bg-[#47F3A0]' },
    airborne: { label: 'AIRBORNE', bg: 'bg-[#47F3A0]/10', text: 'text-[#47F3A0]', border: 'border-[#47F3A0]/30', dot: 'bg-[#47F3A0]' },
    vfr: { label: 'VFR', bg: 'bg-[#47F3A0]/10', text: 'text-[#47F3A0]', border: 'border-[#47F3A0]/30', dot: 'bg-[#47F3A0]' },
    warning: { label: 'WARNING', bg: 'bg-[#FFC857]/10', text: 'text-[#FFC857]', border: 'border-[#FFC857]/30', dot: 'bg-[#FFC857]' },
    ground: { label: 'ON GROUND', bg: 'bg-[#FFC857]/10', text: 'text-[#FFC857]', border: 'border-[#FFC857]/30', dot: 'bg-[#FFC857]' },
    offline: { label: 'OFFLINE', bg: 'bg-[#5A6475]/10', text: 'text-[#B0BAC8]', border: 'border-[#5A6475]/30', dot: 'bg-[#5A6475]' },
    error: { label: 'ERROR', bg: 'bg-[#FF5D5D]/10', text: 'text-[#FF5D5D]', border: 'border-[#FF5D5D]/30', dot: 'bg-[#FF5D5D]' },
    ifr: { label: 'IFR', bg: 'bg-[#FF5D5D]/10', text: 'text-[#FF5D5D]', border: 'border-[#FF5D5D]/30', dot: 'bg-[#FF5D5D]' },
  };

  const activeConfig = config[status] || config.offline;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[11px] font-mono font-semibold tracking-wider ${activeConfig.bg} ${activeConfig.text} ${activeConfig.border} ${className}`}
    >
      <span className="relative flex h-2 w-2">
        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${activeConfig.dot}`} />
        <span className={`relative inline-flex rounded-full h-2 w-2 ${activeConfig.dot}`} />
      </span>
      {customLabel || activeConfig.label}
    </span>
  );
};
