import axios from 'axios';
import type { Role, Permission, RoleListResponse } from '@/types/auth';

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

interface RoleCreateData {
  name: string;
  display_name: string;
  description?: string;
  permission_ids?: string[];
  is_active?: boolean;
}

interface RoleUpdateData {
  name?: string;
  display_name?: string;
  description?: string;
  permission_ids?: string[];
  is_active?: boolean;
}

interface RoleListParams {
  skip?: number;
  limit?: number;
  is_active?: boolean;
}

export const roleAPI = {
  list: async (params?: RoleListParams): Promise<RoleListResponse> => {
    const response = await apiClient.get('/roles', { params });
    return response.data;
  },
  get: async (id: string): Promise<Role> => {
    const response = await apiClient.get(`/roles/${id}`);
    return response.data;
  },
  create: async (data: RoleCreateData): Promise<Role> => {
    const response = await apiClient.post('/roles', data);
    return response.data;
  },
  update: async (id: string, data: RoleUpdateData): Promise<Role> => {
    const response = await apiClient.put(`/roles/${id}`, data);
    return response.data;
  },
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/roles/${id}`);
  },
  getPermissions: async (): Promise<Permission[]> => {
    const response = await apiClient.get('/permissions');
    return response.data;
  },
  addPermission: async (roleId: string, permissionId: string): Promise<void> => {
    await apiClient.post(`/roles/${roleId}/permissions/${permissionId}`);
  },
  removePermission: async (roleId: string, permissionId: string): Promise<void> => {
    await apiClient.delete(`/roles/${roleId}/permissions/${permissionId}`);
  },
};
