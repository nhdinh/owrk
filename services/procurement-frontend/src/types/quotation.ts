export enum QuotationStatus {
  PENDING = 'PENDING',
  ACCEPTED = 'ACCEPTED',
  REJECTED = 'REJECTED',
}

export interface QuotationItem {
  id?: number;
  product_name: string;
  product_description?: string;
  quantity: number;
  unit: string;
  unit_price: number;
  total_price: number;
}

export interface Quotation {
  id: number;
  quotation_code: string;
  purchase_request_id: number;
  purchase_request?: {
    id: number;
    request_code: string;
    title: string;
  };
  vendor_id: number;
  vendor?: {
    id: number;
    vendor_code: string;
    name: string;
  };
  quotation_date: string;
  valid_until?: string;
  total_amount: number;
  tax_amount?: number;
  discount_amount?: number;
  final_amount: number;
  payment_terms?: string;
  delivery_terms?: string;
  warranty_terms?: string;
  status: QuotationStatus;
  notes?: string;
  accepted_by?: number;
  accepted_at?: string;
  rejected_by?: number;
  rejected_at?: string;
  rejection_reason?: string;
  items: QuotationItem[];
  created_at: string;
  updated_at: string;
}

export interface QuotationCreate {
  purchase_request_id: number;
  vendor_id: number;
  quotation_date: string;
  valid_until?: string;
  tax_amount?: number;
  discount_amount?: number;
  payment_terms?: string;
  delivery_terms?: string;
  warranty_terms?: string;
  notes?: string;
  items: Omit<QuotationItem, 'id'>[];
}

export interface QuotationUpdate {
  quotation_date?: string;
  valid_until?: string;
  tax_amount?: number;
  discount_amount?: number;
  payment_terms?: string;
  delivery_terms?: string;
  warranty_terms?: string;
  notes?: string;
  items?: Omit<QuotationItem, 'id'>[];
}

export interface QuotationFilter {
  status?: QuotationStatus;
  purchase_request_id?: number;
  vendor_id?: number;
  date_from?: string;
  date_to?: string;
  skip?: number;
  limit?: number;
}

export interface QuotationComparison {
  purchase_request: {
    id: number;
    request_code: string;
    title: string;
  };
  quotations: Array<{
    id: number;
    quotation_code: string;
    vendor: {
      id: number;
      name: string;
      rating?: number;
    };
    final_amount: number;
    delivery_terms?: string;
    warranty_terms?: string;
    valid_until?: string;
    items: QuotationItem[];
  }>;
}
