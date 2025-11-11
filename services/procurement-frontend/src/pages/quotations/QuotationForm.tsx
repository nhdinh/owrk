import { useNavigate, useParams } from 'react-router-dom';
import { useQuotation, useCreateQuotation, useUpdateQuotation } from '@/hooks/useQuotations';
import { usePurchaseRequests } from '@/hooks/usePurchaseRequests';
import { useVendors } from '@/hooks/useVendors';
import { PurchaseRequestStatus, VendorStatus } from '@/types';
import { useState, useEffect } from 'react';

export default function QuotationForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const { data: existingQuotation } = useQuotation(id!);
  const { data: purchaseRequestsData } = usePurchaseRequests({ status: PurchaseRequestStatus.APPROVED, limit: 100 });
  const { data: vendorsData } = useVendors({ status: VendorStatus.ACTIVE, limit: 100 });
  const createMutation = useCreateQuotation();
  const updateMutation = useUpdateQuotation();

  const [formData, setFormData] = useState({
    purchase_request_id: 0,
    vendor_id: 0,
    quotation_date: new Date().toISOString().split('T')[0],
    valid_until: '',
    tax_amount: 0,
    discount_amount: 0,
    payment_terms: '',
    delivery_terms: '',
    warranty_terms: '',
    notes: '',
    items: [{ product_name: '', product_description: '', quantity: 1, unit: 'pcs', unit_price: 0 }],
  });

  useEffect(() => {
    if (existingQuotation) {
      setFormData({
        purchase_request_id: existingQuotation.purchase_request_id,
        vendor_id: existingQuotation.vendor_id,
        quotation_date: existingQuotation.quotation_date.split('T')[0],
        valid_until: existingQuotation.valid_until ? existingQuotation.valid_until.split('T')[0] : '',
        tax_amount: existingQuotation.tax_amount || 0,
        discount_amount: existingQuotation.discount_amount || 0,
        payment_terms: existingQuotation.payment_terms || '',
        delivery_terms: existingQuotation.delivery_terms || '',
        warranty_terms: existingQuotation.warranty_terms || '',
        notes: existingQuotation.notes || '',
        items: existingQuotation.items.map(item => ({
          product_name: item.product_name,
          product_description: item.product_description || '',
          quantity: item.quantity,
          unit: item.unit,
          unit_price: item.unit_price,
        })),
      });
    }
  }, [existingQuotation]);

  const calculateTotals = () => {
    const total_amount = formData.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
    const final_amount = total_amount + formData.tax_amount - formData.discount_amount;
    return { total_amount, final_amount };
  };

  const { total_amount, final_amount } = calculateTotals();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const items = formData.items.map(item => ({
      ...item,
      total_price: item.quantity * item.unit_price,
    }));

    const submitData: any = {
      ...formData,
      items,
    };

    // Remove empty optional fields
    if (!submitData.valid_until) delete submitData.valid_until;
    if (!submitData.payment_terms) delete submitData.payment_terms;
    if (!submitData.delivery_terms) delete submitData.delivery_terms;
    if (!submitData.warranty_terms) delete submitData.warranty_terms;
    if (!submitData.notes) delete submitData.notes;
    if (submitData.tax_amount === 0) delete submitData.tax_amount;
    if (submitData.discount_amount === 0) delete submitData.discount_amount;

    try {
      if (isEdit && id) {
        await updateMutation.mutateAsync({
          id: parseInt(id),
          data: submitData,
        });
      } else {
        await createMutation.mutateAsync(submitData);
      }
      navigate('/quotations');
    } catch (error) {
      console.error('Failed to save quotation:', error);
    }
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { product_name: '', product_description: '', quantity: 1, unit: 'pcs', unit_price: 0 }],
    });
  };

  const removeItem = (index: number) => {
    setFormData({
      ...formData,
      items: formData.items.filter((_, i) => i !== index),
    });
  };

  const updateItem = (index: number, field: string, value: any) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, items: newItems });
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">
          {isEdit ? 'Edit Quotation' : 'Create Quotation'}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-card rounded-lg border p-6">
            <h2 className="text-xl font-semibold mb-4">Basic Information</h2>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Purchase Request *</label>
                  <select
                    value={formData.purchase_request_id}
                    onChange={(e) => setFormData({ ...formData, purchase_request_id: parseInt(e.target.value) })}
                    required
                    disabled={isEdit}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:bg-muted"
                  >
                    <option value={0}>Select Purchase Request</option>
                    {purchaseRequestsData?.items.map((pr) => (
                      <option key={pr.id} value={pr.id}>
                        {pr.request_code} - {pr.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Vendor *</label>
                  <select
                    value={formData.vendor_id}
                    onChange={(e) => setFormData({ ...formData, vendor_id: parseInt(e.target.value) })}
                    required
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value={0}>Select Vendor</option>
                    {vendorsData?.items.map((vendor) => (
                      <option key={vendor.id} value={vendor.id}>
                        {vendor.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Quotation Date *</label>
                  <input
                    type="date"
                    value={formData.quotation_date}
                    onChange={(e) => setFormData({ ...formData, quotation_date: e.target.value })}
                    required
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Valid Until</label>
                  <input
                    type="date"
                    value={formData.valid_until}
                    onChange={(e) => setFormData({ ...formData, valid_until: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-card rounded-lg border p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Items</h2>
              <button
                type="button"
                onClick={addItem}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
              >
                Add Item
              </button>
            </div>

            <div className="space-y-4">
              {formData.items.map((item, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-medium">Item {index + 1}</h3>
                    {formData.items.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeItem(index)}
                        className="text-destructive hover:underline text-sm"
                      >
                        Remove
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="col-span-2">
                      <label className="block text-sm font-medium mb-1">Product Name *</label>
                      <input
                        type="text"
                        value={item.product_name}
                        onChange={(e) => updateItem(index, 'product_name', e.target.value)}
                        required
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>

                    <div className="col-span-2">
                      <label className="block text-sm font-medium mb-1">Product Description</label>
                      <input
                        type="text"
                        value={item.product_description}
                        onChange={(e) => updateItem(index, 'product_description', e.target.value)}
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-1">Quantity *</label>
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                        required
                        min="1"
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-1">Unit *</label>
                      <input
                        type="text"
                        value={item.unit}
                        onChange={(e) => updateItem(index, 'unit', e.target.value)}
                        required
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-1">Unit Price *</label>
                      <input
                        type="number"
                        value={item.unit_price}
                        onChange={(e) => updateItem(index, 'unit_price', parseFloat(e.target.value) || 0)}
                        required
                        step="0.01"
                        min="0"
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-1">Total</label>
                      <input
                        type="text"
                        value={`$${(item.quantity * item.unit_price).toFixed(2)}`}
                        disabled
                        className="w-full px-3 py-2 border rounded-lg bg-muted"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-card rounded-lg border p-6">
            <h2 className="text-xl font-semibold mb-4">Amounts & Terms</h2>

            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Total Amount</label>
                  <input
                    type="text"
                    value={`$${total_amount.toFixed(2)}`}
                    disabled
                    className="w-full px-3 py-2 border rounded-lg bg-muted font-medium"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Tax Amount</label>
                  <input
                    type="number"
                    value={formData.tax_amount}
                    onChange={(e) => setFormData({ ...formData, tax_amount: parseFloat(e.target.value) || 0 })}
                    step="0.01"
                    min="0"
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Discount Amount</label>
                  <input
                    type="number"
                    value={formData.discount_amount}
                    onChange={(e) => setFormData({ ...formData, discount_amount: parseFloat(e.target.value) || 0 })}
                    step="0.01"
                    min="0"
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-lg">Final Amount</label>
                <input
                  type="text"
                  value={`$${final_amount.toFixed(2)}`}
                  disabled
                  className="w-full px-3 py-2 border-2 rounded-lg bg-primary/10 font-bold text-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Payment Terms</label>
                <textarea
                  value={formData.payment_terms}
                  onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  rows={2}
                  placeholder="e.g., Net 30 days"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Delivery Terms</label>
                <textarea
                  value={formData.delivery_terms}
                  onChange={(e) => setFormData({ ...formData, delivery_terms: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  rows={2}
                  placeholder="e.g., FOB, delivery within 14 days"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Warranty Terms</label>
                <textarea
                  value={formData.warranty_terms}
                  onChange={(e) => setFormData({ ...formData, warranty_terms: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  rows={2}
                  placeholder="e.g., 1 year manufacturer warranty"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  rows={3}
                />
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
            >
              {isEdit ? 'Update' : 'Create'} Quotation
            </button>
            <button
              type="button"
              onClick={() => navigate('/quotations')}
              className="px-6 py-2 border rounded-lg hover:bg-muted"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
