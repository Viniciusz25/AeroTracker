import type { FC } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/organisms/Sidebar';
import { Toolbar } from '../components/organisms/Toolbar';
import { StatusBar } from '../components/organisms/StatusBar';

export const AppLayout: FC = () => {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#050608] text-white">
      {/* Sidebar Navigation Organism */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header Toolbar Organism */}
        <Toolbar />

        {/* Dynamic Route Content */}
        <main className="flex-1 overflow-y-auto bg-[#050608] relative">
          <Outlet />
        </main>

        {/* Footer StatusBar Organism */}
        <StatusBar />
      </div>
    </div>
  );
};
