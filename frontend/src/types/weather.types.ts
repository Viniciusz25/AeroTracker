export interface WeatherConditionObj {
  code?: number;
  main?: string;
  description?: string;
  icon?: string;
  group?: string;
}

export interface WeatherSnapshot {
  location?: string;
  location_name?: string;
  temperature_c: number;
  feels_like_c: number;
  humidity_pct: number;
  pressure_hpa: number;
  wind_speed_ms?: number;
  wind_direction_deg?: number;
  visibility_m?: number;
  condition: string | WeatherConditionObj;
  icon_code?: string;
  metar?: string;
  flight_category?: 'VFR' | 'MVFR' | 'IFR' | 'LIFR';
  updated_at?: string;
}

export interface WeatherResponse {
  status: string;
  data: WeatherSnapshot;
}
