import type { FC } from 'react';
import { Outlet } from 'react-router-dom';

export const AppLayout: FC = () => {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#050608] text-white">
      {/* Sidebar placeholder until Phase 5 */}
      <aside className="w-64 bg-[#0C0E12] border-r border-[#1A1F2B] flex flex-col">
        <div className="p-4 border-b border-[#1A1F2B] flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#47F3A0]/10 border border-[#47F3A0]/30 flex items-center justify-center text-[#47F3A0] font-bold text-sm font-['Outfit']">
            AT
          </div>
          <div>
            <h1 className="font-['Outfit'] font-bold text-sm text-white tracking-wide">AeroTracker Core</h1>
            <p className="text-[10px] text-[#5A6475] font-mono">v2.0.0 · GRU STATION</p>
          </div>
        </div>
        <div className="p-3 text-xs text-[#5A6475] uppercase tracking-wider font-mono font-semibold">
          Navigation
        </div>
      </aside>

      {/* Main Content Container */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header/Toolbar placeholder */}
        <header className="h-14 bg-[#0C0E12]/80 border-b border-[#1A1F2B] backdrop-blur-md px-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#47F3A0] animate-pulse"></span>
            <span className="text-xs font-mono text-[#B0BAC8]">API ONLINE · PORT 8001</span>
          </div>
        </header>

        {/* Page Content Outlet */}
        <main className="flex-1 overflow-y-auto bg-[#050608]">
          <Outlet />
        </main>

        {/* Bottom StatusBar placeholder */}
        <footer className="h-8 bg-[#0C0E12] border-t border-[#1A1F2B] px-4 flex items-center justify-between text-xs text-[#5A6475] font-mono">
          <div>LAT: -23.4356° · LON: -46.4731° (10km RADIUS)</div>
          <div>SYSTEM NOMINAL</div>
        </footer>
      </div>
    </div>
  );
};
