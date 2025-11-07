export * from './purchase-request';
export * from './vendor';
export * from './quotation';
export * from './purchase-order';

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface ApiError {
  detail: string;
  status?: number;
}
