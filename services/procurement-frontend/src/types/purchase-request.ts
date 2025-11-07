export enum PurchaseRequestStatus {
  DRAFT = 'DRAFT',
  PENDING = 'PENDING',
  APPROVED_L1 = 'APPROVED_L1',
  APPROVED_L2 = 'APPROVED_L2',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  CANCELLED = 'CANCELLED',
}

export enum PurchaseRequestPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  URGENT = 'URGENT',
}

export interface PurchaseRequestItem {
  id?: number;
  item_name: string;
  description?: string;
  quantity: number;
  unit: string;
  estimated_unit_price?: number;
  estimated_total_price?: number;
  specification?: string;
  notes?: string;
}

export interface PurchaseRequest {
  id: number;
  request_code: string;
  title: string;
  description?: string;
  department_id: number;
  department?: {
    id: number;
    name: string;
    code: string;
  };
  requester_id: number;
  requester?: {
    id: number;
    email: string;
    full_name: string;
  };
  status: PurchaseRequestStatus;
  priority: PurchaseRequestPriority;
  request_date: string;
  required_date?: string;
  justification?: string;
  budget_code?: string;
  total_estimated_amount?: number;
  approved_by_l1?: number;
  approved_at_l1?: string;
  approved_by_l2?: number;
  approved_at_l2?: string;
  approved_by_final?: number;
  approved_at_final?: string;
  rejected_by?: number;
  rejected_at?: string;
  rejection_reason?: string;
  items: PurchaseRequestItem[];
  created_at: string;
  updated_at: string;
}

export interface PurchaseRequestCreate {
  title: string;
  description?: string;
  department_id: number;
  priority: PurchaseRequestPriority;
  required_date?: string;
  justification?: string;
  budget_code?: string;
  items: Omit<PurchaseRequestItem, 'id'>[];
}

export interface PurchaseRequestUpdate {
  title?: string;
  description?: string;
  priority?: PurchaseRequestPriority;
  required_date?: string;
  justification?: string;
  budget_code?: string;
  items?: Omit<PurchaseRequestItem, 'id'>[];
}

export interface PurchaseRequestFilter {
  status?: PurchaseRequestStatus;
  priority?: PurchaseRequestPriority;
  department_id?: number;
  requester_id?: number;
  date_from?: string;
  date_to?: string;
  search?: string;
  skip?: number;
  limit?: number;
}
