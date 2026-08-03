import { create } from 'zustand';

interface SettingsStore {
  locationName: string;
  latitude: number;
  longitude: number;
  radiusKm: number;
  timezone: string;
  soundEnabled: boolean;
  autoRefreshInterval: number;
  updateLocation: (name: string, lat: number, lon: number) => void;
  setRadiusKm: (radius: number) => void;
  toggleSound: () => void;
}

export const useSettingsStore = create<SettingsStore>((set) => ({
  locationName: 'Guarulhos Airport (GRU)',
  latitude: -23.4356,
  longitude: -46.4731,
  radiusKm: 10,
  timezone: 'America/Sao_Paulo',
  soundEnabled: true,
  autoRefreshInterval: 3,
  updateLocation: (name, lat, lon) => set({ locationName: name, latitude: lat, longitude: lon }),
  setRadiusKm: (radius) => set({ radiusKm: radius }),
  toggleSound: () => set((state) => ({ soundEnabled: !state.soundEnabled })),
}));
