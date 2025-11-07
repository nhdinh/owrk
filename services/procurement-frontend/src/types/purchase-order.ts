export enum PurchaseOrderStatus {
  DRAFT = 'DRAFT',
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  SENT = 'SENT',
  PARTIALLY_RECEIVED = 'PARTIALLY_RECEIVED',
  RECEIVED = 'RECEIVED',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
}

export interface PurchaseOrderItem {
  id?: number;
  product_name: string;
  product_description?: string;
  quantity: number;
  unit: string;
  unit_price: number;
  total_price: number;
  received_quantity?: number;
}

export interface PurchaseOrder {
  id: number;
  po_code: string;
  purchase_request_id: number;
  purchase_request?: {
    id: number;
    request_code: string;
    title: string;
  };
  quotation_id: number;
  quotation?: {
    id: number;
    quotation_code: string;
  };
  vendor_id: number;
  vendor?: {
    id: number;
    vendor_code: string;
    name: string;
    contact_person?: string;
    email?: string;
    phone?: string;
  };
  order_date: string;
  expected_delivery_date?: string;
  actual_delivery_date?: string;
  total_amount: number;
  tax_amount?: number;
  discount_amount?: number;
  shipping_cost?: number;
  final_amount: number;
  payment_terms?: string;
  delivery_address?: string;
  billing_address?: string;
  status: PurchaseOrderStatus;
  notes?: string;
  approved_by?: number;
  approved_at?: string;
  items: PurchaseOrderItem[];
  created_at: string;
  updated_at: string;
}

export interface PurchaseOrderCreate {
  purchase_request_id: number;
  quotation_id: number;
  order_date: string;
  expected_delivery_date?: string;
  tax_amount?: number;
  discount_amount?: number;
  shipping_cost?: number;
  payment_terms?: string;
  delivery_address?: string;
  billing_address?: string;
  notes?: string;
}

export interface PurchaseOrderUpdate {
  expected_delivery_date?: string;
  actual_delivery_date?: string;
  tax_amount?: number;
  discount_amount?: number;
  shipping_cost?: number;
  payment_terms?: string;
  delivery_address?: string;
  billing_address?: string;
  notes?: string;
  status?: PurchaseOrderStatus;
}

export interface PurchaseOrderFilter {
  status?: PurchaseOrderStatus;
  vendor_id?: number;
  purchase_request_id?: number;
  date_from?: string;
  date_to?: string;
  search?: string;
  skip?: number;
  limit?: number;
}
