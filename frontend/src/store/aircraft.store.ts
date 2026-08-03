import { create } from 'zustand';
import type { AircraftState } from '../types/aircraft.types';

interface AircraftStore {
  aircraft: AircraftState[];
  selectedIcao: string | null;
  selectedAircraft: AircraftState | null;
  radarRangeKm: number;
  totalCount: number;
  airborneCount: number;
  onGroundCount: number;
  lastUpdate: string | null;
  setAircraftList: (
    aircraft: AircraftState[],
    total: number,
    airborne: number,
    ground: number
  ) => void;
  selectAircraft: (icao24: string | null) => void;
  setRadarRangeKm: (range: number) => void;
}

export const useAircraftStore = create<AircraftStore>((set, get) => ({
  aircraft: [],
  selectedIcao: null,
  selectedAircraft: null,
  radarRangeKm: 10,
  totalCount: 0,
  airborneCount: 0,
  onGroundCount: 0,
  lastUpdate: null,
  setAircraftList: (aircraft, total, airborne, ground) =>
    set({
      aircraft,
      totalCount: total,
      airborneCount: airborne,
      onGroundCount: ground,
      lastUpdate: new Date().toISOString(),
      selectedAircraft: get().selectedIcao
        ? aircraft.find((a) => a.icao24 === get().selectedIcao) || get().selectedAircraft
        : null,
    }),
  selectAircraft: (icao24) => {
    const list = get().aircraft;
    const found = list.find((a) => a.icao24 === icao24) || null;
    set({ selectedIcao: icao24, selectedAircraft: found });
  },
  setRadarRangeKm: (range) => set({ radarRangeKm: range }),
}));
