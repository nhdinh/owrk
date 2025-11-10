import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

export interface FrameworkContract {
  id: number;
  contract_code: string;
  contract_name: string;
  vendor_id: number;
  vendor?: {
    id: number;
    vendor_code: string;
    vendor_name: string;
  };
  contract_value: number;
  start_date: string;
  end_date: string;
  terms_and_conditions?: string;
  payment_terms?: string;
  delivery_terms?: string;
  contract_file_url?: string;
  status: 'active' | 'expired' | 'terminated';
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface ContractFormData {
  contract_name: string;
  vendor_id: number;
  contract_value: number;
  start_date: string;
  end_date: string;
  terms_and_conditions?: string;
  payment_terms?: string;
  delivery_terms?: string;
  contract_file_url?: string;
}

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  skip: number;
  limit: number;
}

interface ContractFilters {
  skip?: number;
  limit?: number;
  status?: string;
  vendor_id?: number;
  from_date?: string;
  to_date?: string;
}

export const useFrameworkContracts = (filters: ContractFilters = {}) => {
  const params = new URLSearchParams();
  if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
  if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
  if (filters.status) params.append('status', filters.status);
  if (filters.vendor_id) params.append('vendor_id', filters.vendor_id.toString());
  if (filters.from_date) params.append('from_date', filters.from_date);
  if (filters.to_date) params.append('to_date', filters.to_date);

  return useQuery({
    queryKey: ['framework-contracts', filters],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<FrameworkContract>>(
        `/procurement/framework-contracts/?${params.toString()}`
      );
      return response.data;
    },
  });
};

export const useFrameworkContract = (id: number | string) => {
  return useQuery({
    queryKey: ['framework-contract', id],
    queryFn: async () => {
      const response = await api.get<FrameworkContract>(
        `/procurement/framework-contracts/${id}/`
      );
      return response.data;
    },
    enabled: !!id,
  });
};

export const useExpiringContracts = (days: number = 30) => {
  return useQuery({
    queryKey: ['expiring-contracts', days],
    queryFn: async () => {
      const response = await api.get<FrameworkContract[]>(
        `/procurement/framework-contracts/expiring/?days=${days}`
      );
      return response.data;
    },
  });
};

export const useVendorContracts = (vendorId: number) => {
  return useQuery({
    queryKey: ['vendor-contracts', vendorId],
    queryFn: async () => {
      const response = await api.get<FrameworkContract[]>(
        `/procurement/framework-contracts/vendor/${vendorId}/`
      );
      return response.data;
    },
    enabled: !!vendorId,
  });
};

export const useCreateContract = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ContractFormData) => {
      const response = await api.post<FrameworkContract>(
        '/procurement/framework-contracts/',
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['framework-contracts'] });
    },
  });
};

export const useUpdateContract = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<ContractFormData> }) => {
      const response = await api.put<FrameworkContract>(
        `/procurement/framework-contracts/${id}/`,
        data
      );
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['framework-contracts'] });
      queryClient.invalidateQueries({ queryKey: ['framework-contract', variables.id] });
    },
  });
};

export const useDeleteContract = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/procurement/framework-contracts/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['framework-contracts'] });
    },
  });
};

export const useActivateContract = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await api.post<FrameworkContract>(
        `/procurement/framework-contracts/${id}/activate/`
      );
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['framework-contracts'] });
      queryClient.invalidateQueries({ queryKey: ['framework-contract', id] });
    },
  });
};

export const useSuspendContract = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await api.post<FrameworkContract>(
        `/procurement/framework-contracts/${id}/suspend/`
      );
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['framework-contracts'] });
      queryClient.invalidateQueries({ queryKey: ['framework-contract', id] });
    },
  });
};

export const useTerminateContract = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, reason }: { id: number; reason: string }) => {
      const response = await api.post<FrameworkContract>(
        `/procurement/framework-contracts/${id}/terminate/`,
        { reason }
      );
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['framework-contracts'] });
      queryClient.invalidateQueries({ queryKey: ['framework-contract', variables.id] });
    },
  });
};
