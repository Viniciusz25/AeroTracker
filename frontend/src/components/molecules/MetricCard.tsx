import type { FC, ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

export interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  icon?: LucideIcon;
  trend?: {
    value: string;
    positive?: boolean;
  };
  variant?: 'primary' | 'secondary' | 'attention' | 'danger' | 'neutral';
  children?: ReactNode;
  className?: string;
}

export const MetricCard: FC<MetricCardProps> = ({
  label,
  value,
  unit,
  icon: IconComponent,
  trend,
  variant = 'neutral',
  children,
  className = '',
}) => {
  const borderGlow = {
    primary: 'hover:border-[#47F3A0]/40 hover:shadow-[0_0_15px_rgba(71,243,160,0.15)]',
    secondary: 'hover:border-[#33A8FF]/40 hover:shadow-[0_0_15px_rgba(51,168,255,0.15)]',
    attention: 'hover:border-[#FFC857]/40 hover:shadow-[0_0_15px_rgba(255,200,87,0.15)]',
    danger: 'hover:border-[#FF5D5D]/40 hover:shadow-[0_0_15px_rgba(255,93,93,0.15)]',
    neutral: 'hover:border-[#242C3A]',
  };

  const iconColor = {
    primary: 'text-[#47F3A0] bg-[#47F3A0]/10 border-[#47F3A0]/20',
    secondary: 'text-[#33A8FF] bg-[#33A8FF]/10 border-[#33A8FF]/20',
    attention: 'text-[#FFC857] bg-[#FFC857]/10 border-[#FFC857]/20',
    danger: 'text-[#FF5D5D] bg-[#FF5D5D]/10 border-[#FF5D5D]/20',
    neutral: 'text-[#B0BAC8] bg-[#181D25] border-[#242C3A]',
  };

  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ duration: 0.15 }}
      className={`bg-[#131720] border border-[#1A1F2B] rounded-xl p-4 flex flex-col justify-between transition-all duration-200 backdrop-blur-md ${borderGlow[variant]} ${className}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-[#B0BAC8] uppercase tracking-wider font-mono">
          {label}
        </span>
        {IconComponent && (
          <div
            className={`w-8 h-8 rounded-lg border flex items-center justify-center ${iconColor[variant]}`}
          >
            <IconComponent size={16} />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-1.5">
        <span className="font-['Outfit'] font-bold text-2xl md:text-3xl text-white tracking-tight">
          {value}
        </span>
        {unit && <span className="font-mono text-xs text-[#5A6475]">{unit}</span>}
      </div>

      {(trend || children) && (
        <div className="mt-2 pt-2 border-t border-[#1A1F2B] flex items-center justify-between text-xs font-mono">
          {trend && (
            <span
              className={trend.positive ? 'text-[#47F3A0]' : 'text-[#FF5D5D]'}
            >
              {trend.positive ? '▲' : '▼'} {trend.value}
            </span>
          )}
          {children}
        </div>
      )}
    </motion.div>
  );
};
