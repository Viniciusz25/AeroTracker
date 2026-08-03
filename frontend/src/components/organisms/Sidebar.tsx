import type { FC } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Radar,
  Plane,
  Cloud,
  Clock,
  Satellite,
  Moon,
  Globe,
  Radio,
  Rocket,
  Settings,
  Activity,
  ChevronLeft,
  ChevronRight,
  Shield,
} from 'lucide-react';
import { useUIStore } from '../../store/ui.store';
import { useAircraftStore } from '../../store/aircraft.store';
import { NavItem } from '../molecules/NavItem';

interface NavModule {
  id: string;
  path: string;
  label: string;
  icon: typeof LayoutDashboard;
  badge?: () => number | string | undefined;
}

export const Sidebar: FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const airborneCount = useAircraftStore((s) => s.airborneCount);

  const modules: NavModule[] = [
    { id: 'dashboard', path: '/', label: 'Mission Control', icon: LayoutDashboard },
    {
      id: 'radar',
      path: '/radar',
      label: 'Air Traffic Radar',
      icon: Radar,
      badge: () => (airborneCount > 0 ? airborneCount : undefined),
    },
    { id: 'flights', path: '/flights', label: 'Flight Tracker', icon: Plane },
    { id: 'weather', path: '/weather', label: 'Aviation Weather', icon: Cloud },
    { id: 'clock', path: '/clock', label: 'Master Clock', icon: Clock },
    { id: 'iss', path: '/iss', label: 'ISS Tracker', icon: Satellite },
    { id: 'moon', path: '/moon', label: 'Lunar Observatory', icon: Moon },
    { id: 'solar_system', path: '/solar-system', label: 'Solar Ephemeris', icon: Globe },
    { id: 'satellites', path: '/satellites', label: 'Satellites', icon: Radio },
    { id: 'launches', path: '/launches', label: 'Space Launches', icon: Rocket },
    { id: 'settings', path: '/settings', label: 'System Settings', icon: Settings },
    { id: 'diagnostics', path: '/diagnostics', label: 'Diagnostics', icon: Activity },
  ];

  return (
    <aside
      className={`relative bg-[#0C0E12] border-r border-[#1A1F2B] flex flex-col transition-all duration-300 z-30 select-none ${
        sidebarOpen ? 'w-64' : 'w-20'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 px-4 border-b border-[#1A1F2B] flex items-center justify-between">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-10 h-10 rounded-xl bg-[#47F3A0]/10 border border-[#47F3A0]/30 flex items-center justify-center text-[#47F3A0] font-bold font-['Outfit'] text-base shadow-[0_0_12px_rgba(71,243,160,0.15)] shrink-0">
            <Shield size={20} className="text-[#47F3A0]" />
          </div>
          {sidebarOpen && (
            <div className="flex flex-col min-w-0">
              <h1 className="font-['Outfit'] font-bold text-sm text-white tracking-wide truncate">
                AeroTracker
              </h1>
              <span className="text-[10px] font-mono text-[#47F3A0] tracking-widest uppercase">
                CORE v2.0
              </span>
            </div>
          )}
        </div>

        <button
          onClick={toggleSidebar}
          className="p-1.5 rounded-lg text-[#5A6475] hover:text-white hover:bg-[#181D25] transition-colors cursor-pointer"
        >
          {sidebarOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </button>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        {sidebarOpen && (
          <div className="px-3 py-2 text-[10px] font-mono font-bold text-[#5A6475] uppercase tracking-widest">
            Modules
          </div>
        )}
        {modules.map((mod) => {
          const isActive =
            mod.path === '/'
              ? location.pathname === '/'
              : location.pathname.startsWith(mod.path);

          return (
            <NavItem
              key={mod.id}
              label={sidebarOpen ? mod.label : ''}
              icon={mod.icon}
              active={isActive}
              badge={sidebarOpen && mod.badge ? mod.badge() : undefined}
              onClick={() => navigate(mod.path)}
            />
          );
        })}
      </div>

      {/* Footer Profile/Station badge */}
      {sidebarOpen && (
        <div className="p-3 border-t border-[#1A1F2B] bg-[#050608]/50">
          <div className="flex items-center gap-2.5 px-2 py-1.5">
            <span className="w-2 h-2 rounded-full bg-[#47F3A0] animate-pulse" />
            <div className="flex flex-col text-xs font-mono">
              <span className="text-white font-semibold">SBGR / GRU</span>
              <span className="text-[10px] text-[#5A6475]">SECTOR 01 · 10km</span>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
};
