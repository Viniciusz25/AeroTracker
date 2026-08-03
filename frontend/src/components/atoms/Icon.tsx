import type { FC } from 'react';
import type { LucideIcon } from 'lucide-react';

export interface IconProps {
  icon: LucideIcon;
  size?: number;
  color?: 'primary' | 'secondary' | 'attention' | 'danger' | 'muted' | 'white' | 'cyan';
  className?: string;
}

export const Icon: FC<IconProps> = ({
  icon: IconComponent,
  size = 18,
  color = 'muted',
  className = '',
}) => {
  const colorMap = {
    primary: 'text-[#47F3A0]',
    secondary: 'text-[#33A8FF]',
    attention: 'text-[#FFC857]',
    danger: 'text-[#FF5D5D]',
    muted: 'text-[#5A6475]',
    white: 'text-white',
    cyan: 'text-[#00D4FF]',
  };

  return <IconComponent size={size} className={`${colorMap[color]} ${className}`} />;
};
