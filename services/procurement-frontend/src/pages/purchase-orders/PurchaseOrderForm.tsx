import { useNavigate, useParams } from 'react-router-dom';
import { usePurchaseOrder, useCreatePurchaseOrder, useUpdatePurchaseOrder } from '@/hooks/usePurchaseOrders';
import { usePurchaseRequests } from '@/hooks/usePurchaseRequests';
import { useQuotations } from '@/hooks/useQuotations';
import { useQuotation } from '@/hooks/useQuotations';
import { PurchaseRequestStatus, QuotationStatus } from '@/types';
import { useState, useEffect } from 'react';

export default function PurchaseOrderForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const { data: existingPO } = usePurchaseOrder(id!);
  const { data: purchaseRequestsData } = usePurchaseRequests({ status: PurchaseRequestStatus.APPROVED, limit: 100 });
  const createMutation = useCreatePurchaseOrder();
  const updateMutation = useUpdatePurchaseOrder();

  const [formData, setFormData] = useState({
    purchase_request_id: 0,
    quotation_id: 0,
    order_date: new Date().toISOString().split('T')[0],
    expected_delivery_date: '',
    tax_amount: 0,
    discount_amount: 0,
    shipping_cost: 0,
    payment_terms: '',
    delivery_address: '',
    billing_address: '',
    notes: '',
  });

  const [selectedPRId, setSelectedPRId] = useState<number>(0);

  // Fetch quotations for selected PR
  const { data: quotationsData } = useQuotations(
    selectedPRId ? { purchase_request_id: selectedPRId, status: QuotationStatus.ACCEPTED, limit: 100 } : undefined
  );

  // Fetch selected quotation details
  const { data: selectedQuotation } = useQuotation(formData.quotation_id);

  useEffect(() => {
    if (existingPO) {
      setFormData({
        purchase_request_id: existingPO.purchase_request_id,
        quotation_id: existingPO.quotation_id,
        order_date: existingPO.order_date.split('T')[0],
        expected_delivery_date: existingPO.expected_delivery_date ? existingPO.expected_delivery_date.split('T')[0] : '',
        tax_amount: existingPO.tax_amount || 0,
        discount_amount: existingPO.discount_amount || 0,
        shipping_cost: existingPO.shipping_cost || 0,
        payment_terms: existingPO.payment_terms || '',
        delivery_address: existingPO.delivery_address || '',
        billing_address: existingPO.billing_address || '',
        notes: existingPO.notes || '',
      });
      setSelectedPRId(existingPO.purchase_request_id);
    }
  }, [existingPO]);

  // Auto-populate fields from quotation
  useEffect(() => {
    if (selectedQuotation && !isEdit) {
      setFormData(prev => ({
        ...prev,
        tax_amount: selectedQuotation.tax_amount || 0,
        discount_amount: selectedQuotation.discount_amount || 0,
        payment_terms: selectedQuotation.payment_terms || '',
      }));
    }
  }, [selectedQuotation, isEdit]);

  const calculateFinalAmount = () => {
    if (!selectedQuotation) return 0;
    return selectedQuotation.total_amount +
      formData.tax_amount -
      formData.discount_amount +
      formData.shipping_cost;
  };

  const finalAmount = calculateFinalAmount();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const submitData: any = {
      ...formData,
    };

    // Remove empty optional fields
    if (!submitData.expected_delivery_date) delete submitData.expected_delivery_date;
    if (!submitData.payment_terms) delete submitData.payment_terms;
    if (!submitData.delivery_address) delete submitData.delivery_address;
    if (!submitData.billing_address) delete submitData.billing_address;
    if (!submitData.notes) delete submitData.notes;
    if (submitData.tax_amount === 0) delete submitData.tax_amount;
    if (submitData.discount_amount === 0) delete submitData.discount_amount;
    if (submitData.shipping_cost === 0) delete submitData.shipping_cost;

    try {
      if (isEdit && id) {
        await updateMutation.mutateAsync({
          id: parseInt(id),
          data: submitData,
        });
      } else {
        await createMutation.mutateAsync(submitData);
      }
      navigate('/purchase-orders');
    } catch (error) {
      console.error('Failed to save purchase order:', error);
    }
  };

  const handlePRChange = (prId: number) => {
    setSelectedPRId(prId);
    setFormData({ ...formData, purchase_request_id: prId, quotation_id: 0 });
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">
          {isEdit ? 'Edit Purchase Order' : 'Create Purchase Order'}
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
                    onChange={(e) => handlePRChange(parseInt(e.target.value))}
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
                  <label className="block text-sm font-medium mb-2">Quotation (Accepted) *</label>
                  <select
                    value={formData.quotation_id}
                    onChange={(e) => setFormData({ ...formData, quotation_id: parseInt(e.target.value) })}
                    required
                    disabled={!selectedPRId || isEdit}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary disabled:bg-muted"
                  >
                    <option value={0}>Select Quotation</option>
                    {quotationsData?.items.map((quotation) => (
                      <option key={quotation.id} value={quotation.id}>
                        {quotation.quotation_code} - {quotation.vendor?.name} - ${quotation.final_amount.toFixed(2)}
                      </option>
                    ))}
                  </select>
                  {selectedPRId && quotationsData?.items.length === 0 && (
                    <p className="text-sm text-red-600 mt-1">No accepted quotations found for this PR</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Order Date *</label>
                  <input
                    type="date"
                    value={formData.order_date}
                    onChange={(e) => setFormData({ ...formData, order_date: e.target.value })}
                    required
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Expected Delivery Date</label>
                  <input
                    type="date"
                    value={formData.expected_delivery_date}
                    onChange={(e) => setFormData({ ...formData, expected_delivery_date: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Quotation Details (Read-only) */}
          {selectedQuotation && (
            <div className="bg-card rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">Quotation Details (From Selected Quotation)</h2>

              <div className="mb-4">
                <p className="text-sm text-muted-foreground mb-2">Vendor</p>
                <p className="font-medium">{selectedQuotation.vendor?.name}</p>
              </div>

              <div className="mb-4">
                <h3 className="font-semibold mb-2">Items</h3>
                <table className="w-full border rounded-lg text-sm">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-3 py-2 text-left">Product</th>
                      <th className="px-3 py-2 text-right">Qty</th>
                      <th className="px-3 py-2 text-left">Unit</th>
                      <th className="px-3 py-2 text-right">Price</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {selectedQuotation.items.map((item, index) => (
                      <tr key={index}>
                        <td className="px-3 py-2">{item.product_name}</td>
                        <td className="px-3 py-2 text-right">{item.quantity}</td>
                        <td className="px-3 py-2">{item.unit}</td>
                        <td className="px-3 py-2 text-right">${item.total_price.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="bg-muted/50 rounded-lg p-3">
                <p className="text-sm text-muted-foreground">Quotation Total Amount</p>
                <p className="text-lg font-bold">${selectedQuotation.total_amount.toFixed(2)}</p>
              </div>
            </div>
          )}

          <div className="bg-card rounded-lg border p-6">
            <h2 className="text-xl font-semibold mb-4">Amounts & Terms</h2>

            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
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

                <div>
                  <label className="block text-sm font-medium mb-2">Shipping Cost</label>
                  <input
                    type="number"
                    value={formData.shipping_cost}
                    onChange={(e) => setFormData({ ...formData, shipping_cost: parseFloat(e.target.value) || 0 })}
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
                  value={`$${finalAmount.toFixed(2)}`}
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

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Delivery Address</label>
                  <textarea
                    value={formData.delivery_address}
                    onChange={(e) => setFormData({ ...formData, delivery_address: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    rows={3}
                    placeholder="Enter delivery address..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Billing Address</label>
                  <textarea
                    value={formData.billing_address}
                    onChange={(e) => setFormData({ ...formData, billing_address: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    rows={3}
                    placeholder="Enter billing address..."
                  />
                </div>
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
              disabled={createMutation.isPending || updateMutation.isPending || !formData.quotation_id}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
            >
              {isEdit ? 'Update' : 'Create'} Purchase Order
            </button>
            <button
              type="button"
              onClick={() => navigate('/purchase-orders')}
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
