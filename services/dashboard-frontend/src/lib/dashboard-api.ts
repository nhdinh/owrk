import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

export interface SystemStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  total_roles: number;
  users_with_mfa: number;
}

export interface AssetStats {
  total_assets: number;
  available_assets: number;
  assigned_assets: number;
  in_maintenance_assets: number;
  disposed_assets: number;
}

export interface DashboardOverview {
  system_stats: SystemStats;
  asset_stats: AssetStats;
  recent_activity: any[];
}

export interface SystemHealth {
  service: string;
  status: 'healthy' | 'degraded' | 'down';
  response_time_ms?: number;
  last_check: string;
}

export interface DashboardHealth {
  services: SystemHealth[];
  overall_status: 'healthy' | 'degraded' | 'down';
}

export const dashboardAPI = {
  getOverview: async (): Promise<DashboardOverview> => {
    const response = await apiClient.get('/dashboard/overview');
    return response.data;
  },

  getSystemStats: async (): Promise<SystemStats> => {
    const response = await apiClient.get('/dashboard/stats/system');
    return response.data;
  },

  getAssetStats: async (): Promise<AssetStats> => {
    const response = await apiClient.get('/dashboard/stats/assets');
    return response.data;
  },

  getHealth: async (): Promise<DashboardHealth> => {
    const response = await apiClient.get('/dashboard/health');
    return response.data;
  },
};
