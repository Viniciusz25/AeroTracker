import type { FC, ReactNode } from 'react';

export interface BadgeProps {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  size?: 'sm' | 'md';
  pulse?: boolean;
  children: ReactNode;
  className?: string;
}

export const Badge: FC<BadgeProps> = ({
  variant = 'neutral',
  size = 'md',
  pulse = false,
  children,
  className = '',
}) => {
  const variantStyles = {
    success: 'bg-[#47F3A0]/10 text-[#47F3A0] border-[#47F3A0]/30',
    warning: 'bg-[#FFC857]/10 text-[#FFC857] border-[#FFC857]/30',
    danger: 'bg-[#FF5D5D]/10 text-[#FF5D5D] border-[#FF5D5D]/30',
    info: 'bg-[#33A8FF]/10 text-[#33A8FF] border-[#33A8FF]/30',
    neutral: 'bg-[#181D25] text-[#B0BAC8] border-[#242C3A]',
  };

  const dotColor = {
    success: 'bg-[#47F3A0]',
    warning: 'bg-[#FFC857]',
    danger: 'bg-[#FF5D5D]',
    info: 'bg-[#33A8FF]',
    neutral: 'bg-[#B0BAC8]',
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-xs',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono font-medium border rounded-full backdrop-blur-sm select-none ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {pulse && (
        <span className="relative flex h-2 w-2">
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dotColor[variant]}`}
          />
          <span
            className={`relative inline-flex rounded-full h-2 w-2 ${dotColor[variant]}`}
          />
        </span>
      )}
      {children}
    </span>
  );
};
