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
  parent_id?: number;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
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

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
}

export interface Assignment {
  id: number;
  asset_id: number;
  user_id: number;
  department_id: number;
  assigned_date: string;
  assigned_by: number;
  notes?: string;
  returned_date?: string;
  returned_by?: number;
  return_condition?: string;
  return_notes?: string;
  status: string;
  created_at: string;
}

export interface AssignmentCreateRequest {
  user_id: number;
  department_id: number;
  assigned_date: string;
  notes?: string;
}

export interface AssignmentReturnRequest {
  returned_date: string;
  return_condition: string;
  return_notes?: string;
}

export enum MaintenanceType {
  PREVENTIVE = "preventive",
  CORRECTIVE = "corrective",
  EMERGENCY = "emergency",
  ROUTINE = "routine",
}

export enum MaintenanceStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
}

export interface MaintenanceRecord {
  id: number;
  asset_id: number;
  asset_code?: string;
  asset_name?: string;
  maintenance_type: string;
  maintenance_date: string;
  completed_date?: string;
  cost: number;
  technician?: string;
  description?: string;
  notes?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface MaintenanceCreateRequest {
  asset_id: number;
  maintenance_type: string;
  maintenance_date: string;
  description?: string;
  cost?: number;
  technician?: string;
  notes?: string;
}

export interface MaintenanceUpdateRequest {
  maintenance_type?: string;
  maintenance_date?: string;
  completed_date?: string;
  cost?: number;
  technician?: string;
  description?: string;
  notes?: string;
  status?: string;
}
