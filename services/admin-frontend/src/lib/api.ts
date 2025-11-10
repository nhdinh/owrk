import axios from 'axios';

const API_BASE_URL = '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

// Admin API endpoints
export const adminAPI = {
  // Trash Management
  trash: {
    list: (params?: any) => api.get('/admin/trash/', { params }),
    stats: () => api.get('/admin/trash/stats'),
    get: (id: number) => api.get(`/admin/trash/${id}`),
    restore: (id: number, data: any) => api.post(`/admin/trash/${id}/restore`, data),
    permanentDelete: (id: number, data: any) => api.delete(`/admin/trash/${id}`, { data }),
  },

  // Trash Config
  trashConfig: {
    list: (params?: any) => api.get('/admin/trash/config/', { params }),
    get: (module: string, resource: string) =>
      api.get(`/admin/trash/config/${module}/${resource}`),
    update: (id: number, data: any) => api.put(`/admin/trash/config/${id}`, data),
  },

  // Module Settings
  settings: {
    list: (params?: any) => api.get('/admin/module-settings/', { params }),
    getByModule: (module: string) => api.get(`/admin/module-settings/module/${module}`),
    get: (id: number) => api.get(`/admin/module-settings/${id}`),
    create: (data: any) => api.post('/admin/module-settings/', data),
    update: (id: number, data: any) => api.put(`/admin/module-settings/${id}`, data),
    delete: (id: number) => api.delete(`/admin/module-settings/${id}`),
  },
};
