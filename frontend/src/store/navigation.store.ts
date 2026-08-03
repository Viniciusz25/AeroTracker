import { create } from 'zustand';

export type ModuleId =
  | 'dashboard'
  | 'radar'
  | 'flights'
  | 'weather'
  | 'clock'
  | 'iss'
  | 'moon'
  | 'solar_system'
  | 'satellites'
  | 'launches'
  | 'settings'
  | 'diagnostics';

interface NavigationStore {
  activeModule: ModuleId;
  setActiveModule: (module: ModuleId) => void;
}

export const useNavigationStore = create<NavigationStore>((set) => ({
  activeModule: 'dashboard',
  setActiveModule: (module) => set({ activeModule: module }),
}));
