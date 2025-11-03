export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  role?: Role;
}

export interface Role {
  id: number;
  name: string;
  display_name: string;
}
