import { useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchWeather } from '../services/weather.service';
import { useWeatherStore } from '../store/weather.store';
import { useWebSocket } from './useWebSocket';
import type { WeatherResponse } from '../types/weather.types';

export function useWeatherData() {
  const { setWeather } = useWeatherStore();

  const query = useQuery<WeatherResponse>({
    queryKey: ['weather'],
    queryFn: async () => {
      const res = await fetchWeather();
      if (res && res.data) {
        setWeather(res.data);
      }
      return res;
    },
    staleTime: 60000,
    refetchInterval: 60000,
  });

  const handleWsMessage = useCallback(
    (message: any) => {
      if (message?.event === 'weather.updated' && message?.data) {
        setWeather(message.data);
      }
    },
    [setWeather]
  );

  useWebSocket('weather', handleWsMessage);

  return query;
}
