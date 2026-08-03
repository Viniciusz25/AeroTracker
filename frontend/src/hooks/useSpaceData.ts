import { useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchISS, fetchLaunches, fetchNasaApod } from '../services/space.service';
import { useSpaceStore } from '../store/space.store';
import { useWebSocket } from './useWebSocket';

export function useSpaceData() {
  const { setISSPosition, setLaunches, setApod } = useSpaceStore();

  const issQuery = useQuery({
    queryKey: ['iss'],
    queryFn: async () => {
      const res = await fetchISS();
      if (res && res.data) setISSPosition(res.data);
      return res;
    },
    refetchInterval: 5000,
  });

  const launchesQuery = useQuery({
    queryKey: ['launches'],
    queryFn: async () => {
      const res = await fetchLaunches();
      if (res && res.launches) setLaunches(res.launches);
      return res;
    },
    staleTime: 300000,
  });

  const apodQuery = useQuery({
    queryKey: ['nasa-apod'],
    queryFn: async () => {
      const res = await fetchNasaApod();
      if (res && res.data) setApod(res.data);
      return res;
    },
    staleTime: 3600000,
  });

  const handleISSWs = useCallback(
    (msg: any) => {
      if (msg?.event === 'iss.updated' && msg?.data) setISSPosition(msg.data);
    },
    [setISSPosition]
  );

  useWebSocket('iss', handleISSWs);

  return { issQuery, launchesQuery, apodQuery };
}
