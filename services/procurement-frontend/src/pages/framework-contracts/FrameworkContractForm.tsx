import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useFrameworkContract,
  useCreateContract,
  useUpdateContract,
} from '@/hooks/useFrameworkContracts';
import { useVendors } from '@/hooks/useVendors';

export default function FrameworkContractForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const { data: contract } = useFrameworkContract(id!);
  const { data: vendorsData } = useVendors({ limit: 1000 });
  const createMutation = useCreateContract();
  const updateMutation = useUpdateContract();

  const [formData, setFormData] = useState({
    contract_name: '',
    vendor_id: 0,
    contract_value: '',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    terms_and_conditions: '',
    payment_terms: '',
    delivery_terms: '',
    contract_file_url: '',
  });

  useEffect(() => {
    if (contract) {
      setFormData({
        contract_name: contract.contract_name,
        vendor_id: contract.vendor_id,
        contract_value: contract.contract_value.toString(),
        start_date: contract.start_date,
        end_date: contract.end_date,
        terms_and_conditions: contract.terms_and_conditions || '',
        payment_terms: contract.payment_terms || '',
        delivery_terms: contract.delivery_terms || '',
        contract_file_url: contract.contract_file_url || '',
      });
    }
  }, [contract]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const submitData: any = {
      contract_name: formData.contract_name,
      vendor_id: formData.vendor_id,
      contract_value: parseFloat(formData.contract_value),
      start_date: formData.start_date,
      end_date: formData.end_date,
    };

    if (formData.terms_and_conditions) submitData.terms_and_conditions = formData.terms_and_conditions;
    if (formData.payment_terms) submitData.payment_terms = formData.payment_terms;
    if (formData.delivery_terms) submitData.delivery_terms = formData.delivery_terms;
    if (formData.contract_file_url) submitData.contract_file_url = formData.contract_file_url;

    try {
      if (isEdit && id) {
        await updateMutation.mutateAsync({
          id: parseInt(id),
          data: submitData,
        });
      } else {
        await createMutation.mutateAsync(submitData);
      }
      navigate('/framework-contracts');
    } catch (error) {
      console.error('Failed to save contract:', error);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">
          {isEdit ? 'Edit Framework Contract' : 'New Framework Contract'}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-card rounded-lg border border-border p-6">
            <h2 className="text-xl font-semibold mb-4">Contract Information</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Contract Name *</label>
                <input
                  type="text"
                  value={formData.contract_name}
                  onChange={(e) => setFormData({ ...formData, contract_name: e.target.value })}
                  required
                  placeholder="e.g., IT Equipment Supply Agreement 2025"
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Vendor *</label>
                <select
                  value={formData.vendor_id}
                  onChange={(e) => setFormData({ ...formData, vendor_id: parseInt(e.target.value) })}
                  required
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value={0}>Select a vendor</option>
                  {vendorsData?.data.map((vendor) => (
                    <option key={vendor.id} value={vendor.id}>
                      {vendor.vendor_name} ({vendor.vendor_code})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Contract Value ($) *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.contract_value}
                    onChange={(e) => setFormData({ ...formData, contract_value: e.target.value })}
                    required
                    placeholder="0.00"
                    className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Contract Period *</label>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-muted-foreground mb-1">Start Date</label>
                    <input
                      type="date"
                      value={formData.start_date}
                      onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                      required
                      className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-muted-foreground mb-1">End Date</label>
                    <input
                      type="date"
                      value={formData.end_date}
                      onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                      required
                      className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-card rounded-lg border border-border p-6">
            <h2 className="text-xl font-semibold mb-4">Terms and Conditions</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Payment Terms</label>
                <textarea
                  value={formData.payment_terms}
                  onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value })}
                  placeholder="e.g., Net 30 days from invoice date..."
                  rows={3}
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Delivery Terms</label>
                <textarea
                  value={formData.delivery_terms}
                  onChange={(e) => setFormData({ ...formData, delivery_terms: e.target.value })}
                  placeholder="e.g., FOB destination, 5-7 business days..."
                  rows={3}
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Terms and Conditions</label>
                <textarea
                  value={formData.terms_and_conditions}
                  onChange={(e) => setFormData({ ...formData, terms_and_conditions: e.target.value })}
                  placeholder="Enter general terms and conditions..."
                  rows={6}
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Contract Document URL</label>
                <input
                  type="url"
                  value={formData.contract_file_url}
                  onChange={(e) => setFormData({ ...formData, contract_file_url: e.target.value })}
                  placeholder="https://..."
                  className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  URL to the signed contract document (optional)
                </p>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => navigate('/framework-contracts')}
              className="px-6 py-2 border border-input rounded-lg hover:bg-accent"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isEdit ? 'Update Contract' : 'Create Contract'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
