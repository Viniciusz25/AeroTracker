export interface WeatherSnapshot {
  location: string;
  temperature_c: number;
  feels_like_c: number;
  humidity_pct: number;
  pressure_hpa: number;
  wind_speed_ms: number;
  wind_direction_deg: number;
  visibility_m: number;
  condition: string;
  icon_code: string;
  metar?: string;
  flight_category?: 'VFR' | 'MVFR' | 'IFR' | 'LIFR';
  updated_at: string;
}

export interface WeatherResponse {
  status: string;
  data: WeatherSnapshot;
}
