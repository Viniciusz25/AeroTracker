import type { FC, ReactNode } from 'react';
import { motion, type HTMLMotionProps } from 'framer-motion';

export interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  icon?: ReactNode;
  children?: ReactNode;
  isLoading?: boolean;
}

export const Button: FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  icon,
  children,
  isLoading = false,
  disabled,
  className = '',
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-150 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed select-none cursor-pointer';

  const sizeStyles = {
    sm: 'px-2.5 py-1.5 text-xs gap-1.5',
    md: 'px-3.5 py-2 text-sm gap-2',
    lg: 'px-5 py-2.5 text-base gap-2.5',
  };

  const variantStyles = {
    primary:
      'bg-[#47F3A0] text-[#050608] hover:bg-[#3be090] active:bg-[#2bb87a] shadow-[0_0_12px_rgba(71,243,160,0.2)] font-semibold',
    secondary:
      'bg-[#181D25] text-white hover:bg-[#242C3A] border border-[#242C3A] active:bg-[#1A1F2B]',
    ghost:
      'bg-transparent text-[#B0BAC8] hover:text-white hover:bg-[#181D25] active:bg-[#1A1F2B]',
    danger:
      'bg-[#FF5D5D]/10 text-[#FF5D5D] hover:bg-[#FF5D5D]/20 border border-[#FF5D5D]/30 active:bg-[#FF5D5D]/30',
    outline:
      'bg-transparent text-[#47F3A0] border border-[#47F3A0]/40 hover:bg-[#47F3A0]/10 active:bg-[#47F3A0]/20',
  };

  return (
    <motion.button
      whileTap={{ scale: disabled || isLoading ? 1 : 0.97 }}
      disabled={disabled || isLoading}
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {isLoading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : (
        icon
      )}
      {children}
    </motion.button>
  );
};
