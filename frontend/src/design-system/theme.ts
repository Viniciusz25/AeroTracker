import { tokens } from './tokens';

export const theme = {
  tokens,
  cardStyles: 'bg-[#131720] border border-[#1A1F2B] rounded-xl shadow-lg backdrop-blur-md',
  cardHoverStyles: 'hover:border-[#242C3A] hover:bg-[#181D25] transition-all duration-200',
  panelStyles: 'bg-[#0C0E12] border-r border-[#1A1F2B]',
  inputStyles: 'bg-[#0B0E14] border border-[#1A1F2B] rounded-md px-3 py-2 text-white focus:border-[#47F3A0] focus:outline-none transition-colors font-mono text-sm',
  badgeVariants: {
    success: 'bg-[#47F3A0]/10 text-[#47F3A0] border border-[#47F3A0]/30',
    warning: 'bg-[#FFC857]/10 text-[#FFC857] border border-[#FFC857]/30',
    danger: 'bg-[#FF5D5D]/10 text-[#FF5D5D] border border-[#FF5D5D]/30',
    info: 'bg-[#33A8FF]/10 text-[#33A8FF] border border-[#33A8FF]/30',
    neutral: 'bg-[#1A1F2B] text-[#B0BAC8] border border-[#242C3A]',
  },
};
