import type { FC, ReactNode } from 'react';

export interface WidgetGridProps {
  children: ReactNode;
  cols?: 1 | 2 | 3 | 4;
  className?: string;
}

export const WidgetGrid: FC<WidgetGridProps> = ({ children, cols = 3, className = '' }) => {
  const colMap = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };

  return <div className={`grid gap-4 ${colMap[cols]} ${className}`}>{children}</div>;
};
