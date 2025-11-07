export enum VendorStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  BLACKLISTED = 'BLACKLISTED',
}

export interface Vendor {
  id: number;
  vendor_code: string;
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  tax_id?: string;
  status: VendorStatus;
  rating?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface VendorCreate {
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  tax_id?: string;
  status?: VendorStatus;
  rating?: number;
  notes?: string;
}

export interface VendorUpdate {
  name?: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  tax_id?: string;
  status?: VendorStatus;
  rating?: number;
  notes?: string;
}

export interface VendorFilter {
  status?: VendorStatus;
  search?: string;
  skip?: number;
  limit?: number;
}
