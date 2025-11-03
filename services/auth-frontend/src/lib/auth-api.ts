import axios from 'axios';
import type {
  User,
  LoginRequest,
  LoginResponse,
  VerifyOTPRequest,
  AuthTokens,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
  SetupMFAResponse,
  EnableMFARequest,
} from '@/types/auth';

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

    // Don't attempt token refresh for login, OTP verification, or refresh endpoints
    const skipRefreshEndpoints = ['/auth/login', '/auth/verify-otp', '/auth/refresh', '/auth/forgot-password'];
    const shouldSkipRefresh = skipRefreshEndpoints.some(endpoint => originalRequest.url?.includes(endpoint));

    if (error.response?.status === 401 && !originalRequest._retry && !shouldSkipRefresh) {
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
        window.location.href = '/auth/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post('/auth/login', data);
    return response.data;
  },
  verifyOTP: async (data: VerifyOTPRequest): Promise<AuthTokens> => {
    const response = await apiClient.post('/auth/verify-otp', data);
    return response.data;
  },
  me: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },
  refresh: async (refreshToken: string): Promise<AuthTokens> => {
    const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },
  forgotPassword: async (data: ForgotPasswordRequest): Promise<void> => {
    await apiClient.post('/auth/forgot-password', data);
  },
  resetPassword: async (data: ResetPasswordRequest): Promise<void> => {
    await apiClient.post('/auth/reset-password', data);
  },
  changePassword: async (data: ChangePasswordRequest): Promise<void> => {
    await apiClient.post('/users/change-password', data);
  },
  setupMFA: async (): Promise<SetupMFAResponse> => {
    const response = await apiClient.post('/auth/mfa/setup');
    return response.data;
  },
  enableMFA: async (data: EnableMFARequest): Promise<void> => {
    await apiClient.post('/auth/mfa/enable', data);
  },
  disableMFA: async (): Promise<void> => {
    await apiClient.post('/auth/mfa/disable');
  },
};
