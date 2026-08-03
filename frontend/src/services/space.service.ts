import { apiClient } from './api.client';
import type { ISSPosition, LaunchItem, NasaApod } from '../types/space.types';

export async function fetchISS(): Promise<{ status: string; data: ISSPosition }> {
  return await apiClient.get<unknown, { status: string; data: ISSPosition }>('/iss');
}

export async function fetchLaunches(): Promise<{ status: string; launches: LaunchItem[] }> {
  return await apiClient.get<unknown, { status: string; launches: LaunchItem[] }>('/launches');
}

export async function fetchNasaApod(): Promise<{ status: string; data: NasaApod }> {
  return await apiClient.get<unknown, { status: string; data: NasaApod }>('/nasa/apod');
}
