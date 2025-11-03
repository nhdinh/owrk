import axios from 'axios';
import type {
  Asset,
  AssetListParams,
  AssetCreateRequest,
  AssetUpdateRequest,
  AssignAssetRequest,
  Category,
  Assignment,
  AssignmentCreateRequest,
  AssignmentReturnRequest,
  MaintenanceRecord,
  MaintenanceCreateRequest,
  MaintenanceUpdateRequest,
} from '@/types/asset';

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

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');
        const response = await axios.post(`${originalRequest.baseURL}/auth/refresh`, { refresh_token: refreshToken });
        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export interface AssetListResponse {
  assets: Asset[];
  total: number;
  page: number;
  page_size: number;
}

export const assetAPI = {
  // Asset CRUD
  list: async (params?: AssetListParams): Promise<AssetListResponse> => {
    const response = await apiClient.get('/assets', { params });
    return response.data;
  },

  get: async (id: number): Promise<Asset> => {
    const response = await apiClient.get(`/assets/${id}`);
    return response.data;
  },

  create: async (data: AssetCreateRequest): Promise<Asset> => {
    const response = await apiClient.post('/assets', data);
    return response.data;
  },

  update: async (id: number, data: AssetUpdateRequest): Promise<Asset> => {
    const response = await apiClient.put(`/assets/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/assets/${id}`);
  },

  // Assignment
  assign: async (id: number, data: AssignAssetRequest): Promise<Asset> => {
    const response = await apiClient.post(`/assets/${id}/assign`, data);
    return response.data;
  },

  reclaim: async (id: number): Promise<Asset> => {
    const response = await apiClient.post(`/assets/${id}/reclaim`);
    return response.data;
  },

  // Categories
  getCategories: async (): Promise<Category[]> => {
    const response = await apiClient.get('/assets/categories/');
    return response.data;
  },

  getCategory: async (id: number): Promise<Category> => {
    const response = await apiClient.get(`/assets/categories/${id}`);
    return response.data;
  },

  // File management
  uploadFile: async (assetId: number, file: File): Promise<void> => {
    const formData = new FormData();
    formData.append('file', file);
    await apiClient.post(`/assets/${assetId}/files`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  deleteFile: async (assetId: number, fileId: number): Promise<void> => {
    await apiClient.delete(`/assets/${assetId}/files/${fileId}`);
  },

  // Assignments
  listAssignments: async (params?: { status?: string; user_id?: number }): Promise<Assignment[]> => {
    const response = await apiClient.get('/assets/assignments/', { params });
    return response.data;
  },

  assignAsset: async (assetId: number, data: AssignmentCreateRequest): Promise<Assignment> => {
    const response = await apiClient.post(`/assets/${assetId}/assign`, data);
    return response.data;
  },

  returnAsset: async (assetId: number, data: AssignmentReturnRequest): Promise<Assignment> => {
    const response = await apiClient.post(`/assets/${assetId}/return`, data);
    return response.data;
  },

  getAssetHistory: async (assetId: number): Promise<Assignment[]> => {
    const response = await apiClient.get(`/assets/${assetId}/history`);
    return response.data;
  },

  // Maintenance
  listMaintenance: async (params?: { status?: string; asset_id?: number }): Promise<MaintenanceRecord[]> => {
    const response = await apiClient.get('/assets/maintenance/', { params });
    return response.data;
  },

  getMaintenance: async (id: number): Promise<MaintenanceRecord> => {
    const response = await apiClient.get(`/assets/maintenance/${id}`);
    return response.data;
  },

  createMaintenance: async (data: MaintenanceCreateRequest): Promise<MaintenanceRecord> => {
    const response = await apiClient.post('/assets/maintenance/', data);
    return response.data;
  },

  updateMaintenance: async (id: number, data: MaintenanceUpdateRequest): Promise<MaintenanceRecord> => {
    const response = await apiClient.put(`/assets/maintenance/${id}`, data);
    return response.data;
  },

  deleteMaintenance: async (id: number): Promise<void> => {
    await apiClient.delete(`/assets/maintenance/${id}`);
  },

  listAssets: async (params?: AssetListParams): Promise<AssetListResponse> => {
    const response = await apiClient.get('/assets/', { params });
    return response.data;
  },
};
