import { create } from 'zustand';
import type { WeatherSnapshot } from '../types/weather.types';

interface WeatherStore {
  currentWeather: WeatherSnapshot | null;
  setWeather: (data: WeatherSnapshot) => void;
}

export const useWeatherStore = create<WeatherStore>((set) => ({
  currentWeather: null,
  setWeather: (data) => set({ currentWeather: data }),
}));
