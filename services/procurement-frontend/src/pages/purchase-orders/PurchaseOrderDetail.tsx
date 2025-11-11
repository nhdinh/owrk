import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  usePurchaseOrder,
  useApprovePurchaseOrder,
  useSendPurchaseOrder,
  useReceivePurchaseOrder,
  useCancelPurchaseOrder,
  useDeletePurchaseOrder,
} from '@/hooks/usePurchaseOrders';
import { PurchaseOrderStatus } from '@/types';
import { useState } from 'react';

export default function PurchaseOrderDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: po, isLoading, error } = usePurchaseOrder(id!);
  const approveMutation = useApprovePurchaseOrder();
  const sendMutation = useSendPurchaseOrder();
  const receiveMutation = useReceivePurchaseOrder();
  const cancelMutation = useCancelPurchaseOrder();
  const deleteMutation = useDeletePurchaseOrder();

  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [showReceiveDialog, setShowReceiveDialog] = useState(false);
  const [receivedQuantities, setReceivedQuantities] = useState<Record<number, number>>({});

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !po) {
    return (
      <div className="p-8">
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg">
          Error loading purchase order
        </div>
      </div>
    );
  }

  const getStatusColor = (status: PurchaseOrderStatus) => {
    switch (status) {
      case PurchaseOrderStatus.APPROVED:
      case PurchaseOrderStatus.RECEIVED:
      case PurchaseOrderStatus.COMPLETED:
        return 'bg-green-100 text-green-700';
      case PurchaseOrderStatus.CANCELLED:
        return 'bg-red-100 text-red-700';
      case PurchaseOrderStatus.PENDING:
      case PurchaseOrderStatus.PARTIALLY_RECEIVED:
        return 'bg-yellow-100 text-yellow-700';
      case PurchaseOrderStatus.SENT:
        return 'bg-blue-100 text-blue-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const handleApprove = async () => {
    if (window.confirm('Are you sure you want to approve this purchase order?')) {
      try {
        await approveMutation.mutateAsync(po.id);
      } catch (error) {
        console.error('Failed to approve:', error);
      }
    }
  };

  const handleSend = async () => {
    if (window.confirm('Are you sure you want to send this purchase order to the vendor?')) {
      try {
        await sendMutation.mutateAsync(po.id);
      } catch (error) {
        console.error('Failed to send:', error);
      }
    }
  };

  const handleReceive = async () => {
    const items = po.items.map(item => ({
      item_id: item.id!,
      received_quantity: receivedQuantities[item.id!] || item.quantity,
    }));

    try {
      await receiveMutation.mutateAsync({ id: po.id, items });
      setShowReceiveDialog(false);
      setReceivedQuantities({});
    } catch (error) {
      console.error('Failed to receive:', error);
    }
  };

  const handleCancel = async () => {
    if (!cancelReason.trim()) return;
    try {
      await cancelMutation.mutateAsync({ id: po.id, reason: cancelReason });
      setShowCancelDialog(false);
      setCancelReason('');
    } catch (error) {
      console.error('Failed to cancel:', error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this purchase order?')) {
      try {
        await deleteMutation.mutateAsync(po.id);
        navigate('/purchase-orders');
      } catch (error) {
        console.error('Failed to delete:', error);
      }
    }
  };

  return (
    <div className="p-8">
      <div className="mb-6">
        <Link to="/purchase-orders" className="text-primary hover:underline text-sm">
          ← Back to Purchase Orders
        </Link>
      </div>

      <div className="bg-card rounded-lg border p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl font-bold">{po.po_code}</h1>
            <p className="text-muted-foreground mt-1">{po.vendor?.name || 'Unknown Vendor'}</p>
          </div>
          <div className="flex gap-2">
            {po.status === PurchaseOrderStatus.PENDING && (
              <button
                onClick={handleApprove}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Approve
              </button>
            )}
            {po.status === PurchaseOrderStatus.APPROVED && (
              <button
                onClick={handleSend}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Send to Vendor
              </button>
            )}
            {(po.status === PurchaseOrderStatus.SENT || po.status === PurchaseOrderStatus.PARTIALLY_RECEIVED) && (
              <button
                onClick={() => setShowReceiveDialog(true)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Receive Items
              </button>
            )}
            {po.status === PurchaseOrderStatus.DRAFT && (
              <>
                <Link
                  to={`/purchase-orders/${po.id}/edit`}
                  className="px-4 py-2 border rounded-lg hover:bg-muted"
                >
                  Edit
                </Link>
                <button
                  onClick={handleDelete}
                  className="px-4 py-2 border border-destructive text-destructive rounded-lg hover:bg-destructive/10"
                >
                  Delete
                </button>
              </>
            )}
            {po.status !== PurchaseOrderStatus.CANCELLED && po.status !== PurchaseOrderStatus.COMPLETED && (
              <button
                onClick={() => setShowCancelDialog(true)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Cancel
              </button>
            )}
          </div>
        </div>

        {/* Header Info */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <p className="text-sm text-muted-foreground">Purchase Request</p>
            {po.purchase_request ? (
              <Link
                to={`/purchase-requests/${po.purchase_request.id}`}
                className="font-medium text-primary hover:underline"
              >
                {po.purchase_request.request_code} - {po.purchase_request.title}
              </Link>
            ) : <p className="font-medium">-</p>}
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Quotation</p>
            {po.quotation ? (
              <Link
                to={`/quotations/${po.quotation.id}`}
                className="font-medium text-primary hover:underline"
              >
                {po.quotation.quotation_code}
              </Link>
            ) : <p className="font-medium">-</p>}
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Order Date</p>
            <p className="font-medium">{new Date(po.order_date).toLocaleDateString()}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Expected Delivery</p>
            <p className="font-medium">
              {po.expected_delivery_date ? new Date(po.expected_delivery_date).toLocaleDateString() : '-'}
            </p>
          </div>
          {po.actual_delivery_date && (
            <div>
              <p className="text-sm text-muted-foreground">Actual Delivery</p>
              <p className="font-medium">{new Date(po.actual_delivery_date).toLocaleDateString()}</p>
            </div>
          )}
          <div>
            <p className="text-sm text-muted-foreground">Status</p>
            <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(po.status)}`}>
              {po.status}
            </span>
          </div>
        </div>

        {/* Vendor Contact Info */}
        {po.vendor && (
          <div className="bg-muted/50 rounded-lg p-4 mb-6">
            <h3 className="font-semibold mb-2">Vendor Contact Information</h3>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Contact Person</p>
                <p className="text-sm font-medium">{po.vendor.contact_person || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="text-sm font-medium">{po.vendor.email || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Phone</p>
                <p className="text-sm font-medium">{po.vendor.phone || '-'}</p>
              </div>
            </div>
          </div>
        )}

        {/* Items Table */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">Items</h2>
          <table className="w-full border rounded-lg">
            <thead className="bg-muted">
              <tr>
                <th className="px-4 py-2 text-left">Product</th>
                <th className="px-4 py-2 text-right">Quantity</th>
                <th className="px-4 py-2 text-left">Unit</th>
                <th className="px-4 py-2 text-right">Unit Price</th>
                <th className="px-4 py-2 text-right">Total</th>
                <th className="px-4 py-2 text-right">Received</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {po.items.map((item, index) => (
                <tr key={index}>
                  <td className="px-4 py-2">
                    <p className="font-medium">{item.product_name}</p>
                    {item.product_description && (
                      <p className="text-sm text-muted-foreground">{item.product_description}</p>
                    )}
                  </td>
                  <td className="px-4 py-2 text-right">{item.quantity}</td>
                  <td className="px-4 py-2">{item.unit}</td>
                  <td className="px-4 py-2 text-right">${item.unit_price.toFixed(2)}</td>
                  <td className="px-4 py-2 text-right font-medium">${item.total_price.toFixed(2)}</td>
                  <td className="px-4 py-2 text-right">
                    <span className={`font-medium ${
                      item.received_quantity === item.quantity ? 'text-green-600' :
                      (item.received_quantity || 0) > 0 ? 'text-yellow-600' :
                      'text-gray-500'
                    }`}>
                      {item.received_quantity || 0} / {item.quantity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Amounts */}
        <div className="border-t pt-4 mb-6">
          <div className="max-w-md ml-auto space-y-2">
            <div className="flex justify-between">
              <span>Total Amount:</span>
              <span className="font-medium">${po.total_amount.toFixed(2)}</span>
            </div>
            {po.tax_amount !== undefined && po.tax_amount > 0 && (
              <div className="flex justify-between">
                <span>Tax:</span>
                <span className="font-medium">${po.tax_amount.toFixed(2)}</span>
              </div>
            )}
            {po.discount_amount !== undefined && po.discount_amount > 0 && (
              <div className="flex justify-between text-green-600">
                <span>Discount:</span>
                <span className="font-medium">-${po.discount_amount.toFixed(2)}</span>
              </div>
            )}
            {po.shipping_cost !== undefined && po.shipping_cost > 0 && (
              <div className="flex justify-between">
                <span>Shipping:</span>
                <span className="font-medium">${po.shipping_cost.toFixed(2)}</span>
              </div>
            )}
            <div className="flex justify-between text-lg font-bold border-t pt-2">
              <span>Final Amount:</span>
              <span>${po.final_amount.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Addresses & Terms */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {po.delivery_address && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Delivery Address</p>
              <p className="text-sm whitespace-pre-line">{po.delivery_address}</p>
            </div>
          )}
          {po.billing_address && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Billing Address</p>
              <p className="text-sm whitespace-pre-line">{po.billing_address}</p>
            </div>
          )}
          {po.payment_terms && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Payment Terms</p>
              <p className="text-sm">{po.payment_terms}</p>
            </div>
          )}
        </div>

        {po.notes && (
          <div className="mb-6">
            <p className="text-sm text-muted-foreground mb-2">Notes</p>
            <p>{po.notes}</p>
          </div>
        )}

        <div className="border-t pt-4">
          <p className="text-sm text-muted-foreground">
            Created: {new Date(po.created_at).toLocaleString()} |
            Last Updated: {new Date(po.updated_at).toLocaleString()}
            {po.approved_at && ` | Approved: ${new Date(po.approved_at).toLocaleString()}`}
          </p>
        </div>
      </div>

      {/* Cancel Dialog */}
      {showCancelDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold mb-4">Cancel Purchase Order</h2>
            <textarea
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              placeholder="Enter cancellation reason..."
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary min-h-[100px]"
            />
            <div className="flex gap-2 mt-4">
              <button
                onClick={handleCancel}
                disabled={!cancelReason.trim()}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                Cancel PO
              </button>
              <button
                onClick={() => {
                  setShowCancelDialog(false);
                  setCancelReason('');
                }}
                className="px-4 py-2 border rounded-lg hover:bg-muted"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Receive Dialog */}
      {showReceiveDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-lg p-6 max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-semibold mb-4">Receive Items</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Enter the quantity received for each item. Leave unchanged to receive the full ordered quantity.
            </p>
            <table className="w-full border rounded-lg mb-4">
              <thead className="bg-muted">
                <tr>
                  <th className="px-4 py-2 text-left">Product</th>
                  <th className="px-4 py-2 text-right">Ordered</th>
                  <th className="px-4 py-2 text-right">Already Received</th>
                  <th className="px-4 py-2 text-right">Receive Now</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {po.items.map((item) => {
                  const remaining = item.quantity - (item.received_quantity || 0);
                  return (
                    <tr key={item.id}>
                      <td className="px-4 py-2">
                        <p className="font-medium">{item.product_name}</p>
                      </td>
                      <td className="px-4 py-2 text-right">{item.quantity}</td>
                      <td className="px-4 py-2 text-right">{item.received_quantity || 0}</td>
                      <td className="px-4 py-2 text-right">
                        <input
                          type="number"
                          min="0"
                          max={remaining}
                          value={receivedQuantities[item.id!] ?? remaining}
                          onChange={(e) => setReceivedQuantities({
                            ...receivedQuantities,
                            [item.id!]: parseInt(e.target.value) || 0
                          })}
                          className="w-24 px-2 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-primary text-right"
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div className="flex gap-2">
              <button
                onClick={handleReceive}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Confirm Receipt
              </button>
              <button
                onClick={() => {
                  setShowReceiveDialog(false);
                  setReceivedQuantities({});
                }}
                className="px-4 py-2 border rounded-lg hover:bg-muted"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
