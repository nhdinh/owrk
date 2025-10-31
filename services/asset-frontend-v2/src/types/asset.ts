export enum AssetStatus {
  NEW = "new",
  IN_USE = "in_use",
  UNDER_MAINTENANCE = "under_maintenance",
  DAMAGED = "damaged",
  DISPOSED = "disposed",
}

export enum AssetType {
  FIXED_ASSET = "fixed_asset",
  TOOL_EQUIPMENT = "tool_equipment",
}

export interface Category {
  id: number;
  name: string;
  code: string;
  group: string;
  description?: string;
}

export interface Department {
  id: number;
  name: string;
  code: string;
}

export interface AssignedUser {
  user_id: number;
  user_name: string;
  department_id: number;
  department_name: string;
}

export interface AssetFile {
  id: number;
  name: string;
  file_type: string;
  size: number;
  url: string;
  uploaded_at: string;
}

export interface AssignmentHistory {
  id: number;
  assigned_to_user: string;
  assigned_date: string;
  reclaimed_date?: string;
  status: string;
}

export interface MaintenanceHistory {
  id: number;
  type: string;
  date: string;
  cost: number;
  notes?: string;
}

export interface Asset {
  id: number;
  code: string;
  name: string;
  asset_type: AssetType;
  category?: Category;
  category_id?: number;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  year_of_manufacture?: number;
  purchase_price: number;
  purchase_date: string;
  depreciation_method?: string;
  depreciation_years?: number;
  salvage_value?: number;
  current_value?: number;
  warranty_start_date?: string;
  warranty_months?: number;
  warranty_end_date?: string;
  warranty_provider?: string;
  department_id?: number;
  department?: Department;
  location?: string;
  status: AssetStatus;
  assigned_to?: AssignedUser;
  notes?: string;
  files?: AssetFile[];
  assignment_history?: AssignmentHistory[];
  maintenance_history?: MaintenanceHistory[];
  created_at: string;
  updated_at: string;
}

export interface AssetListParams {
  page?: number;
  page_size?: number;
  search?: string;
  category_id?: number;
  asset_type?: AssetType;
  status?: AssetStatus;
  department_id?: number;
  assigned_user_id?: number;
  min_price?: number;
  max_price?: number;
  sort?: string;
}

export interface AssetCreateRequest {
  code: string;
  name: string;
  asset_type: AssetType;
  category_id: number;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  year_of_manufacture?: number;
  purchase_price: number;
  purchase_date: string;
  depreciation_method?: string;
  depreciation_years?: number;
  salvage_value?: number;
  warranty_start_date?: string;
  warranty_months?: number;
  warranty_provider?: string;
  department_id?: number;
  location?: string;
  status: AssetStatus;
  notes?: string;
}

export interface AssetUpdateRequest {
  name?: string;
  category_id?: number;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  year_of_manufacture?: number;
  purchase_price?: number;
  purchase_date?: string;
  depreciation_method?: string;
  depreciation_years?: number;
  salvage_value?: number;
  warranty_start_date?: string;
  warranty_months?: number;
  warranty_provider?: string;
  department_id?: number;
  location?: string;
  status?: AssetStatus;
  notes?: string;
}

export interface AssignAssetRequest {
  user_id: number;
  department_id: number;
  notes?: string;
}
