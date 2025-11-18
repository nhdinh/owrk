export interface User {
  id: string;
  email: string;
  username?: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  email_verified: boolean;
  mfa_enabled: boolean;
  user_type?: string;
  role?: Role;
  role_id?: string;
  department_id?: string;
  phone_number?: string;
  position?: string;
  address?: string;
  last_login_at?: string;
  last_login_ip?: string;
  password_changed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Role {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  permissions?: Permission[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Permission {
  id: string;
  name: string;
  code: string;
  description?: string;
  resource?: string;
  action?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  temp_token: string;
  message: string;
  user?: User;
  requires_mfa: boolean;
  access_token?: string;
  refresh_token?: string;
}

export interface VerifyOTPRequest {
  temp_token: string;
  otp_code: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface SetupMFAResponse {
  secret: string;
  qr_code_url: string;
}

export interface EnableMFARequest {
  otp_code: string;
}

// Paginated response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface UserListResponse extends PaginatedResponse<User> {
  users: User[];
}

export interface RoleListResponse extends PaginatedResponse<Role> {
  roles: Role[];
}
