import { create } from 'zustand';
import type { ISSPosition, LaunchItem, NasaApod } from '../types/space.types';

interface SpaceStore {
  issPosition: ISSPosition | null;
  launches: LaunchItem[];
  apod: NasaApod | null;
  setISSPosition: (data: ISSPosition) => void;
  setLaunches: (launches: LaunchItem[]) => void;
  setApod: (apod: NasaApod) => void;
}

export const useSpaceStore = create<SpaceStore>((set) => ({
  issPosition: null,
  launches: [],
  apod: null,
  setISSPosition: (data) => set({ issPosition: data }),
  setLaunches: (launches) => set({ launches }),
  setApod: (apod) => set({ apod }),
}));
