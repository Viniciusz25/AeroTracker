import { useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAircraft } from '../services/aircraft.service';
import { useAircraftStore } from '../store/aircraft.store';
import { useWebSocket } from './useWebSocket';
import type { AircraftListResponse } from '../types/aircraft.types';

export function useAircraftData() {
  const { setAircraftList } = useAircraftStore();

  // REST initial load & background refetch
  const query = useQuery<AircraftListResponse>({
    queryKey: ['aircraft'],
    queryFn: async () => {
      const res = await fetchAircraft();
      if (res && res.aircraft) {
        setAircraftList(
          res.aircraft,
          res.total_count ?? res.aircraft.length,
          res.airborne_count ?? res.aircraft.filter((a) => !a.on_ground).length,
          res.on_ground_count ?? res.aircraft.filter((a) => a.on_ground).length
        );
      }
      return res;
    },
    refetchInterval: 5000,
  });

  // WebSocket real-time broadcast listener
  const handleWsMessage = useCallback(
    (message: any) => {
      if (message?.event === 'aircraft.updated' && message?.data) {
        const payload = message.data;
        const list = payload.aircraft || [];
        setAircraftList(
          list,
          payload.total_count ?? list.length,
          payload.airborne_count ?? list.filter((a: any) => !a.on_ground).length,
          payload.on_ground_count ?? list.filter((a: any) => a.on_ground).length
        );
      }
    },
    [setAircraftList]
  );

  useWebSocket('aircraft', handleWsMessage);

  return query;
}
