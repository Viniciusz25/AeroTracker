import { apiClient } from './api.client';
import type { WeatherResponse, WeatherSnapshot } from '../types/weather.types';

export async function fetchWeather(): Promise<WeatherResponse> {
  return await apiClient.get<unknown, WeatherResponse>('/weather');
}

export async function fetchWeatherForecast(): Promise<{ status: string; data: WeatherSnapshot[] }> {
  return await apiClient.get<unknown, { status: string; data: WeatherSnapshot[] }>('/weather/forecast');
}
