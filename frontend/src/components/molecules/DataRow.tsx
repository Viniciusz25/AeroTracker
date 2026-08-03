import type { FC, ReactNode } from 'react';

export interface DataRowProps {
  label: string;
  value: ReactNode;
  unit?: string;
  highlight?: boolean;
  className?: string;
}

export const DataRow: FC<DataRowProps> = ({
  label,
  value,
  unit,
  highlight = false,
  className = '',
}) => {
  return (
    <div
      className={`flex items-center justify-between py-2 border-b border-[#1A1F2B] last:border-0 ${className}`}
    >
      <span className="text-xs text-[#B0BAC8] font-medium font-['Inter']">{label}</span>
      <div className="flex items-baseline gap-1 font-mono text-xs">
        <span className={highlight ? 'text-[#47F3A0] font-bold' : 'text-white font-medium'}>
          {value}
        </span>
        {unit && <span className="text-[#5A6475] text-[10px]">{unit}</span>}
      </div>
    </div>
  );
};
