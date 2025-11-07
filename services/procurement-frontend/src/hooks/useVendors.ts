import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import type { Vendor, VendorCreate, VendorUpdate, VendorFilter, PaginatedResponse } from '@/types';

export const useVendors = (filters?: VendorFilter) => {
  return useQuery({
    queryKey: ['vendors', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, String(value));
          }
        });
      }
      const response = await api.get<PaginatedResponse<Vendor>>(
        `/procurement/vendors?${params.toString()}`
      );
      return response.data;
    },
  });
};

export const useVendor = (id: number | string) => {
  return useQuery({
    queryKey: ['vendor', id],
    queryFn: async () => {
      const response = await api.get<Vendor>(`/procurement/vendors/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreateVendor = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: VendorCreate) => {
      const response = await api.post<Vendor>('/procurement/vendors/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
    },
  });
};

export const useUpdateVendor = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: VendorUpdate }) => {
      const response = await api.put<Vendor>(`/procurement/vendors/${id}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
      queryClient.invalidateQueries({ queryKey: ['vendor', variables.id] });
    },
  });
};

export const useDeleteVendor = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/procurement/vendors/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
    },
  });
};
