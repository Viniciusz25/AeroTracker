import type { FC, ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

export interface WidgetCardProps {
  title: string;
  subtitle?: string;
  icon?: LucideIcon;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export const WidgetCard: FC<WidgetCardProps> = ({
  title,
  subtitle,
  icon: IconComponent,
  action,
  children,
  className = '',
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`bg-[#131720] border border-[#1A1F2B] hover:border-[#242C3A] rounded-xl flex flex-col overflow-hidden transition-colors shadow-lg backdrop-blur-md ${className}`}
    >
      {/* Header */}
      <div className="px-4 py-3.5 border-b border-[#1A1F2B] flex items-center justify-between bg-[#0C0E12]/50">
        <div className="flex items-center gap-2.5">
          {IconComponent && <IconComponent size={16} className="text-[#47F3A0]" />}
          <div>
            <h3 className="font-['Outfit'] font-semibold text-sm text-white tracking-wide">
              {title}
            </h3>
            {subtitle && <p className="text-[11px] text-[#B0BAC8] font-['Inter']">{subtitle}</p>}
          </div>
        </div>
        {action && <div>{action}</div>}
      </div>

      {/* Body Content */}
      <div className="p-4 flex-1">{children}</div>
    </motion.div>
  );
};
