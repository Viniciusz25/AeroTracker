import type { FC } from 'react';

export interface SeparatorProps {
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

export const Separator: FC<SeparatorProps> = ({
  orientation = 'horizontal',
  className = '',
}) => {
  if (orientation === 'vertical') {
    return <div className={`w-[1px] h-full bg-[#1A1F2B] self-stretch ${className}`} />;
  }

  return <div className={`h-[1px] w-full bg-[#1A1F2B] my-2 ${className}`} />;
};
