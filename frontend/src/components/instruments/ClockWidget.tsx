import { FC, useState, useEffect } from 'react';

export interface ClockWidgetProps {
  label?: string;
  timezone?: string; // 'UTC' or IANA timezone like 'America/Sao_Paulo'
  className?: string;
}

export const ClockWidget: FC<ClockWidgetProps> = ({
  label = 'UTC MASTER CLOCK',
  timezone = 'UTC',
  className = '',
}) => {
  const [time, setTime] = useState<Date>(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formattedTime = time.toLocaleTimeString('en-US', {
    timeZone: timezone === 'UTC' ? 'UTC' : timezone,
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  const formattedDate = time.toLocaleDateString('en-US', {
    timeZone: timezone === 'UTC' ? 'UTC' : timezone,
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });

  return (
    <div
      className={`bg-[#0C0E12] border border-[#1A1F2B] rounded-xl p-4 flex flex-col items-center justify-center font-mono select-none ${className}`}
    >
      <span className="text-[10px] text-[#5A6475] uppercase tracking-widest font-semibold mb-1">
        {label}
      </span>
      <span className="font-['Outfit'] font-bold text-3xl md:text-4xl text-[#47F3A0] tracking-wider drop-shadow-[0_0_12px_rgba(71,243,160,0.2)]">
        {formattedTime}
      </span>
      <span className="text-xs text-[#B0BAC8] mt-1 tracking-widest uppercase">
        {formattedDate}
      </span>
    </div>
  );
};
