export interface Coordinate {
  latitude: number;
  longitude: number;
}

export interface Altitude {
  value: number;
  unit: string;
  in_meters?: number;
  in_feet?: number;
}

export interface Velocity {
  value: number;
  unit: string;
  in_kmh?: number;
  in_knots?: number;
}

export interface AircraftState {
  icao24: string;
  callsign: string | null;
  origin_country: string | null;
  position: Coordinate | null;
  altitude: Altitude | null;
  velocity: Velocity | null;
  heading: number | null;
  vertical_rate: number | null;
  on_ground: boolean;
  squawk: string | null;
  last_contact: number | null;
  position_source: string;
  category: string;
}

export interface AircraftListResponse {
  status: string;
  total_count: number;
  airborne_count: number;
  on_ground_count: number;
  query_time: number | null;
  aircraft: AircraftState[];
}
