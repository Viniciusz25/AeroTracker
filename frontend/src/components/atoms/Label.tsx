import type { FC, ReactNode } from 'react';

export interface LabelProps {
  variant?: 'display' | 'title' | 'body' | 'caption' | 'mono';
  color?: 'primary' | 'secondary' | 'muted' | 'white' | 'accent' | 'danger';
  children: ReactNode;
  className?: string;
}

export const Label: FC<LabelProps> = ({
  variant = 'body',
  color = 'white',
  children,
  className = '',
}) => {
  const variantMap = {
    display: 'font-["Outfit"] font-bold text-3xl md:text-4xl tracking-tight',
    title: 'font-["Outfit"] font-semibold text-lg md:text-xl tracking-normal',
    body: 'font-["Inter"] text-sm font-normal leading-relaxed',
    caption: 'font-["Inter"] text-xs font-medium text-[#B0BAC8]',
    mono: 'font-mono text-xs font-semibold tracking-wider uppercase',
  };

  const colorMap = {
    primary: 'text-[#47F3A0]',
    secondary: 'text-[#33A8FF]',
    muted: 'text-[#5A6475]',
    white: 'text-white',
    accent: 'text-[#00D4FF]',
    danger: 'text-[#FF5D5D]',
  };

  return <span className={`${variantMap[variant]} ${colorMap[color]} ${className}`}>{children}</span>;
};
