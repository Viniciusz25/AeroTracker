import { apiClient } from './api.client';
import type { AircraftListResponse, AircraftState } from '../types/aircraft.types';

export async function fetchAircraft(): Promise<AircraftListResponse> {
  return await apiClient.get<unknown, AircraftListResponse>('/aircraft');
}

export async function fetchAircraftByIcao(icao24: string): Promise<{ status: string; aircraft: AircraftState }> {
  return await apiClient.get<unknown, { status: string; aircraft: AircraftState }>(`/aircraft/${icao24}`);
}
