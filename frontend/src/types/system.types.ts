export interface SystemHealth {
  status: string;
  version: string;
  uptime_seconds: number;
  active_modules: number;
  timestamp: string;
}

export interface ModuleStatus {
  name: string;
  display_name: string;
  description: string;
  active: boolean;
  interval_seconds: number;
  last_updated?: string | null;
  error?: string | null;
}

export interface SystemStatus {
  status: string;
  version: string;
  uptime_seconds: number;
  location: {
    name: string;
    latitude: number;
    longitude: number;
    timezone: string;
  };
  modules: Record<string, ModuleStatus>;
  websocket: {
    total_connections: number;
    channels: Record<string, number>;
  };
}
