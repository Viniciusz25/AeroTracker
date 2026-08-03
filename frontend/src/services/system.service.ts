import { apiClient } from './api.client';
import type { SystemHealth, SystemStatus, ModuleStatus } from '../types/system.types';

export async function fetchHealth(): Promise<SystemHealth> {
  return await apiClient.get<unknown, SystemHealth>('/health');
}

export async function fetchStatus(): Promise<SystemStatus> {
  return await apiClient.get<unknown, SystemStatus>('/status');
}

export async function fetchModules(): Promise<{ status: string; total: number; active: number; modules: ModuleStatus[] }> {
  return await apiClient.get<unknown, { status: string; total: number; active: number; modules: ModuleStatus[] }>('/modules');
}
