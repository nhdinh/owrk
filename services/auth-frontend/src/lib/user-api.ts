import axios from 'axios';
import type { User, UserListResponse } from '@/types/auth';

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

interface UserCreateData {
  email: string;
  username?: string;
  full_name: string;
  password: string;
  role_id?: number;
  department_id?: number;
  phone_number?: string;
  position?: string;
  address?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

interface UserUpdateData {
  email?: string;
  username?: string;
  full_name?: string;
  role_id?: number;
  department_id?: number;
  phone_number?: string;
  position?: string;
  address?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

interface UserListParams {
  skip?: number;
  limit?: number;
  search?: string;
  role_id?: number;
  department_id?: number;
  is_active?: boolean;
  is_superuser?: boolean;
}

export const userAPI = {
  list: async (params?: UserListParams): Promise<UserListResponse> => {
    const response = await apiClient.get('/users', { params });
    return response.data;
  },
  get: async (id: number): Promise<User> => {
    const response = await apiClient.get(`/users/${id}`);
    return response.data;
  },
  create: async (data: UserCreateData): Promise<User> => {
    const response = await apiClient.post('/users', data);
    return response.data;
  },
  update: async (id: number, data: UserUpdateData): Promise<User> => {
    const response = await apiClient.put(`/users/${id}`, data);
    return response.data;
  },
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/users/${id}`);
  },
  activate: async (id: number): Promise<void> => {
    await apiClient.post(`/users/${id}/activate`);
  },
  deactivate: async (id: number): Promise<void> => {
    await apiClient.post(`/users/${id}/deactivate`);
  },
  resetPassword: async (id: number, newPassword: string): Promise<void> => {
    await apiClient.post(`/users/${id}/reset-password`, { new_password: newPassword });
  },
  unlock: async (id: number): Promise<void> => {
    await apiClient.post(`/users/${id}/unlock`);
  },
};
