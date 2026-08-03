import type { Coordinate } from './aircraft.types';

export interface ISSPosition {
  name: string;
  norad_id: number;
  position: Coordinate;
  altitude_km: number;
  velocity_kmh: number;
  visibility: string;
  footprint_km: number;
  updated_at: string;
}

export interface LaunchNamedObject {
  id?: string | number;
  name?: string;
  abbrev?: string;
  description?: string;
  location?: string;
}

export interface LaunchItem {
  id: string;
  name: string | LaunchNamedObject;
  vehicle: string | LaunchNamedObject;
  provider: string | LaunchNamedObject;
  pad: string | LaunchNamedObject;
  status: string | LaunchNamedObject;
  net: string;
  probability_pct?: number | null;
  mission_type?: string | null;
}

export interface NasaApod {
  title: string;
  date: string;
  explanation: string;
  url: string;
  media_type: string;
  copyright?: string;
}
