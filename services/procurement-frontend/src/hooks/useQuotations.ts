import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import type {
  Quotation,
  QuotationCreate,
  QuotationUpdate,
  QuotationFilter,
  QuotationComparison,
  PaginatedResponse,
} from '@/types';

export const useQuotations = (filters?: QuotationFilter) => {
  return useQuery({
    queryKey: ['quotations', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, String(value));
          }
        });
      }
      const response = await api.get<PaginatedResponse<Quotation>>(
        `/procurement/quotations/?${params.toString()}`
      );
      return response.data;
    },
  });
};

export const useQuotation = (id: number | string) => {
  return useQuery({
    queryKey: ['quotation', id],
    queryFn: async () => {
      const response = await api.get<Quotation>(`/procurement/quotations/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

export const useQuotationComparison = (purchaseRequestId: number | string) => {
  return useQuery({
    queryKey: ['quotation-comparison', purchaseRequestId],
    queryFn: async () => {
      const response = await api.get<QuotationComparison>(
        `/procurement/purchase-requests/${purchaseRequestId}/quotations/comparison`
      );
      return response.data;
    },
    enabled: !!purchaseRequestId,
  });
};

export const useCreateQuotation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: QuotationCreate) => {
      const response = await api.post<Quotation>('/procurement/quotations/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      queryClient.invalidateQueries({ queryKey: ['quotation-comparison'] });
    },
  });
};

export const useUpdateQuotation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: QuotationUpdate }) => {
      const response = await api.put<Quotation>(`/procurement/quotations/${id}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      queryClient.invalidateQueries({ queryKey: ['quotation', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['quotation-comparison'] });
    },
  });
};

export const useDeleteQuotation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/procurement/quotations/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      queryClient.invalidateQueries({ queryKey: ['quotation-comparison'] });
    },
  });
};

export const useAcceptQuotation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await api.post<Quotation>(`/procurement/quotations/${id}/accept`);
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      queryClient.invalidateQueries({ queryKey: ['quotation', id] });
      queryClient.invalidateQueries({ queryKey: ['quotation-comparison'] });
    },
  });
};

export const useRejectQuotation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, reason }: { id: number; reason: string }) => {
      const response = await api.post<Quotation>(`/procurement/quotations/${id}/reject`, { reason });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      queryClient.invalidateQueries({ queryKey: ['quotation', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['quotation-comparison'] });
    },
  });
};
