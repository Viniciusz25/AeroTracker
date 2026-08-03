import type { FC } from 'react';
import type { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

export interface NavItemProps {
  label: string;
  icon: LucideIcon;
  active?: boolean;
  badge?: number | string;
  onClick?: () => void;
  className?: string;
}

export const NavItem: FC<NavItemProps> = ({
  label,
  icon: IconComponent,
  active = false,
  badge,
  onClick,
  className = '',
}) => {
  return (
    <motion.button
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 cursor-pointer select-none ${
        active
          ? 'bg-[#47F3A0]/10 text-[#47F3A0] border border-[#47F3A0]/30 shadow-[0_0_12px_rgba(71,243,160,0.1)]'
          : 'text-[#B0BAC8] hover:text-white hover:bg-[#181D25] border border-transparent'
      } ${className}`}
    >
      <div className="flex items-center gap-3">
        <IconComponent
          size={18}
          className={active ? 'text-[#47F3A0]' : 'text-[#5A6475]'}
        />
        <span className="font-['Outfit']">{label}</span>
      </div>

      {badge !== undefined && (
        <span
          className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
            active
              ? 'bg-[#47F3A0] text-[#050608]'
              : 'bg-[#1A1F2B] text-[#B0BAC8]'
          }`}
        >
          {badge}
        </span>
      )}
    </motion.button>
  );
};
