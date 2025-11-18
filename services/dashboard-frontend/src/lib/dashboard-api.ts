import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

export interface DashboardData {
  period_hours: number;
  statistics: {
    total_services: number;
    healthy_services: number;
    down_services: number;
    average_response_time: number;
    timestamp: number;
  };
  services: ServiceMetrics[];
  total_services: number;
  timestamp: number;
}

export interface ServiceMetrics {
  name: string;
  status: string;
  current_response_time: number;
  address: string;
  port: number;
  uptime_percent: number;
  last_check: number;
}

export interface ServiceStatus {
  name: string;
  hostname: string;
  address: string;
  port: number;
  health_endpoint: string;
  last_check: number;
  response_time: number;
  status: "healthy" | "down" | "stale";
  last_updated: number;
}

export interface UptimeData {
  service_name: string;
  uptime_percent: number;
  period_hours: number;
}

export interface PercentilesData {
  service_name: string;
  p50: number;
  p95: number;
  p99: number;
  period_hours: number;
}

export interface DowntimeEvent {
  start_time: string;
  end_time?: string;
  duration_seconds?: number;
  status: string;
}

export interface HistoryData {
  timestamps: string[];
  values: number[];
  service_name: string;
  field: string;
  aggregation_window: string;
}

export interface ServiceSummary {
  service_name: string;
  period_hours: number;
  uptime_percent: number;
  average_response_time: number;
  percentiles: {
    p50: number;
    p95: number;
    p99: number;
  };
  total_checks: number;
  downtime_events: DowntimeEvent[];
}

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
  status: "healthy" | "degraded" | "down";
  response_time_ms?: number;
  last_check: string;
}

export interface DashboardHealth {
  services: SystemHealth[];
  overall_status: "healthy" | "degraded" | "down";
}

export interface ServiceRegistryStatusResponse {
  name: string;
  hostname: string;
  address: string;
  response_time: number;
  last_check: number;
}

export const dashboardAPI = {
  getOverview: async (): Promise<DashboardOverview> => {
    const response = await apiClient.get("/dashboard/overview");
    return response.data;
  },

  getSystemStats: async (): Promise<SystemStats> => {
    const response = await apiClient.get("/dashboard/stats/system");
    return response.data;
  },

  getAssetStats: async (): Promise<AssetStats> => {
    const response = await apiClient.get("/dashboard/stats/assets");
    return response.data;
  },

  getHealth: async (): Promise<DashboardHealth> => {
    const response = await apiClient.get("/dashboard/health");
    return response.data;
  },
};

export const monitoringAPI = {
  /**
   * Get all registered services
   */
  getServices: async (): Promise<Record<string, ServiceStatus>> => {
    const response = await apiClient.get("/services");
    return response.data;
  },

  /**
   * Get comprehensive dashboard data
   */
  getDashboard: async (hours: number = 24): Promise<DashboardData> => {
    const response = await apiClient.get(
      `/monitoring/dashboard?hours=${hours}`
    );
    return response.data;
  },

  /**
   * Get uptime for a specific service
   */
  getServiceUptime: async (
    serviceName: string,
    hours: number = 24
  ): Promise<UptimeData> => {
    const response = await apiClient.get(
      `/monitoring/uptime/${serviceName}?hours=${hours}`
    );
    return response.data;
  },

  /**
   * Get uptime for all services
   */
  getAllServicesUptime: async (
    hours: number = 24
  ): Promise<{ services: UptimeData[]; period_hours: number }> => {
    const response = await apiClient.get(
      `/monitoring/uptime?hours=${hours}`
    );
    return response.data;
  },

  /**
   * Get response time percentiles for a service
   */
  getPercentiles: async (
    serviceName: string,
    hours: number = 24
  ): Promise<PercentilesData> => {
    const response = await apiClient.get(
      `/monitoring/percentiles/${serviceName}?hours=${hours}`
    );
    return response.data;
  },

  /**
   * Get downtime events for a service
   */
  getDowntimeEvents: async (
    serviceName: string,
    hours: number = 24
  ): Promise<{
    service_name: string;
    downtime_events: DowntimeEvent[];
    period_hours: number;
  }> => {
    const response = await apiClient.get(
      `/monitoring/downtime/${serviceName}?hours=${hours}`
    );
    return response.data;
  },

  /**
   * Get historical data for a service
   */
  getHistory: async (
    serviceName: string,
    hours: number = 24,
    aggregationWindow: string = "1m"
  ): Promise<HistoryData> => {
    const response = await apiClient.get(
      `/monitoring/history/${serviceName}?hours=${hours}&aggregation_window=${aggregationWindow}`
    );
    return response.data;
  },

  /**
   * Get comprehensive metrics summary for a service
   */
  getServiceSummary: async (
    serviceName: string,
    hours: number = 24
  ): Promise<ServiceSummary> => {
    const response = await apiClient.get(
      `/monitoring/summary/${serviceName}?hours=${hours}`
    );
    return response.data;
  },

  /**
   * Manually trigger service health checks
   */
  triggerPing: async (): Promise<{ message: string; ping_logs: string[] }> => {
    const response = await apiClient.get(`/ping`);
    return response.data;
  },
};
