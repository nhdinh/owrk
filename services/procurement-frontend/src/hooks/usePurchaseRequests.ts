import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import type {
  PurchaseRequest,
  PurchaseRequestCreate,
  PurchaseRequestUpdate,
  PurchaseRequestFilter,
  PaginatedResponse,
} from '@/types';

export const usePurchaseRequests = (filters?: PurchaseRequestFilter) => {
  return useQuery({
    queryKey: ['purchase-requests', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, String(value));
          }
        });
      }
      const response = await api.get<PaginatedResponse<PurchaseRequest>>(
        `/procurement/purchase-requests/?${params.toString()}`
      );
      return response.data;
    },
  });
};

export const usePurchaseRequest = (id: number | string) => {
  return useQuery({
    queryKey: ['purchase-request', id],
    queryFn: async () => {
      const response = await api.get<PurchaseRequest>(`/procurement/purchase-requests/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useCreatePurchaseRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: PurchaseRequestCreate) => {
      const response = await api.post<PurchaseRequest>('/procurement/purchase-requests/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-requests'] });
    },
  });
};

export const useUpdatePurchaseRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: PurchaseRequestUpdate }) => {
      const response = await api.put<PurchaseRequest>(`/procurement/purchase-requests/${id}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['purchase-requests'] });
      queryClient.invalidateQueries({ queryKey: ['purchase-request', variables.id] });
    },
  });
};

export const useDeletePurchaseRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/procurement/purchase-requests/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-requests'] });
    },
  });
};

export const useSubmitPurchaseRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await api.post<PurchaseRequest>(`/procurement/purchase-requests/${id}/submit`);
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['purchase-requests'] });
      queryClient.invalidateQueries({ queryKey: ['purchase-request', id] });
    },
  });
};

export const useApprovePurchaseRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, level }: { id: number; level: number }) => {
      const response = await api.post<PurchaseRequest>(
        `/procurement/purchase-requests/${id}/approve?level=${level}`
      );
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['purchase-requests'] });
      queryClient.invalidateQueries({ queryKey: ['purchase-request', variables.id] });
    },
  });
};

export const useRejectPurchaseRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, reason }: { id: number; reason: string }) => {
      const response = await api.post<PurchaseRequest>(`/procurement/purchase-requests/${id}/reject`, {
        reason,
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['purchase-requests'] });
      queryClient.invalidateQueries({ queryKey: ['purchase-request', variables.id] });
    },
  });
};

export const useCancelPurchaseRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await api.post<PurchaseRequest>(`/procurement/purchase-requests/${id}/cancel`);
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['purchase-requests'] });
      queryClient.invalidateQueries({ queryKey: ['purchase-request', id] });
    },
  });
};
