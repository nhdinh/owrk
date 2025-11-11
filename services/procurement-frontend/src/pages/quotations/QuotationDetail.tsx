import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuotation, useAcceptQuotation, useRejectQuotation, useDeleteQuotation } from '@/hooks/useQuotations';
import { QuotationStatus } from '@/types';
import { useState } from 'react';

export default function QuotationDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: quotation, isLoading, error } = useQuotation(id!);
  const acceptMutation = useAcceptQuotation();
  const rejectMutation = useRejectQuotation();
  const deleteMutation = useDeleteQuotation();

  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !quotation) {
    return (
      <div className="p-8">
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg">
          Error loading quotation
        </div>
      </div>
    );
  }

  const handleAccept = async () => {
    if (window.confirm('Are you sure you want to accept this quotation?')) {
      try {
        await acceptMutation.mutateAsync(quotation.id);
      } catch (error) {
        console.error('Failed to accept:', error);
      }
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) return;
    try {
      await rejectMutation.mutateAsync({ id: quotation.id, reason: rejectionReason });
      setShowRejectDialog(false);
      setRejectionReason('');
    } catch (error) {
      console.error('Failed to reject:', error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this quotation?')) {
      try {
        await deleteMutation.mutateAsync(quotation.id);
        navigate('/quotations');
      } catch (error) {
        console.error('Failed to delete:', error);
      }
    }
  };

  return (
    <div className="p-8">
      <div className="mb-6">
        <Link to="/quotations" className="text-primary hover:underline text-sm">
          ← Back to Quotations
        </Link>
      </div>

      <div className="bg-card rounded-lg border p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl font-bold">{quotation.quotation_code}</h1>
            <p className="text-muted-foreground mt-1">
              {quotation.vendor?.name || 'Unknown Vendor'}
            </p>
          </div>
          <div className="flex gap-2">
            {quotation.status === QuotationStatus.PENDING && (
              <>
                <button
                  onClick={handleAccept}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Accept
                </button>
                <button
                  onClick={() => setShowRejectDialog(true)}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Reject
                </button>
                <Link
                  to={`/quotations/${quotation.id}/edit`}
                  className="px-4 py-2 border rounded-lg hover:bg-muted"
                >
                  Edit
                </Link>
              </>
            )}
            {quotation.status === QuotationStatus.PENDING && (
              <button
                onClick={handleDelete}
                className="px-4 py-2 border border-destructive text-destructive rounded-lg hover:bg-destructive/10"
              >
                Delete
              </button>
            )}
          </div>
        </div>

        {/* Header Information */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <p className="text-sm text-muted-foreground">Purchase Request</p>
            {quotation.purchase_request ? (
              <Link
                to={`/purchase-requests/${quotation.purchase_request.id}`}
                className="font-medium text-primary hover:underline"
              >
                {quotation.purchase_request.request_code} - {quotation.purchase_request.title}
              </Link>
            ) : (
              <p className="font-medium">-</p>
            )}
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Vendor</p>
            {quotation.vendor ? (
              <Link
                to={`/vendors/${quotation.vendor.id}`}
                className="font-medium text-primary hover:underline"
              >
                {quotation.vendor.name}
              </Link>
            ) : (
              <p className="font-medium">-</p>
            )}
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Quotation Date</p>
            <p className="font-medium">{new Date(quotation.quotation_date).toLocaleDateString()}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Valid Until</p>
            <p className="font-medium">
              {quotation.valid_until ? new Date(quotation.valid_until).toLocaleDateString() : '-'}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Status</p>
            <span className={`px-2 py-1 text-xs rounded-full ${
              quotation.status === QuotationStatus.ACCEPTED ? 'bg-green-100 text-green-700' :
              quotation.status === QuotationStatus.REJECTED ? 'bg-red-100 text-red-700' :
              'bg-yellow-100 text-yellow-700'
            }`}>
              {quotation.status}
            </span>
          </div>
        </div>

        {/* Items Table */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">Items</h2>
          <table className="w-full border rounded-lg">
            <thead className="bg-muted">
              <tr>
                <th className="px-4 py-2 text-left">Product Name</th>
                <th className="px-4 py-2 text-left">Description</th>
                <th className="px-4 py-2 text-right">Quantity</th>
                <th className="px-4 py-2 text-left">Unit</th>
                <th className="px-4 py-2 text-right">Unit Price</th>
                <th className="px-4 py-2 text-right">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {quotation.items.map((item, index) => (
                <tr key={index}>
                  <td className="px-4 py-2">{item.product_name}</td>
                  <td className="px-4 py-2">{item.product_description || '-'}</td>
                  <td className="px-4 py-2 text-right">{item.quantity}</td>
                  <td className="px-4 py-2">{item.unit}</td>
                  <td className="px-4 py-2 text-right">${item.unit_price.toFixed(2)}</td>
                  <td className="px-4 py-2 text-right font-medium">${item.total_price.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Amount Calculations */}
        <div className="border-t pt-4 mb-6">
          <div className="max-w-md ml-auto space-y-2">
            <div className="flex justify-between">
              <span>Total Amount:</span>
              <span className="font-medium">${quotation.total_amount.toFixed(2)}</span>
            </div>
            {quotation.tax_amount !== undefined && quotation.tax_amount > 0 && (
              <div className="flex justify-between">
                <span>Tax:</span>
                <span className="font-medium">${quotation.tax_amount.toFixed(2)}</span>
              </div>
            )}
            {quotation.discount_amount !== undefined && quotation.discount_amount > 0 && (
              <div className="flex justify-between text-green-600">
                <span>Discount:</span>
                <span className="font-medium">-${quotation.discount_amount.toFixed(2)}</span>
              </div>
            )}
            <div className="flex justify-between text-lg font-bold border-t pt-2">
              <span>Final Amount:</span>
              <span>${quotation.final_amount.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Terms */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {quotation.payment_terms && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Payment Terms</p>
              <p className="text-sm">{quotation.payment_terms}</p>
            </div>
          )}
          {quotation.delivery_terms && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Delivery Terms</p>
              <p className="text-sm">{quotation.delivery_terms}</p>
            </div>
          )}
          {quotation.warranty_terms && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">Warranty Terms</p>
              <p className="text-sm">{quotation.warranty_terms}</p>
            </div>
          )}
        </div>

        {quotation.notes && (
          <div className="mb-6">
            <p className="text-sm text-muted-foreground mb-2">Notes</p>
            <p>{quotation.notes}</p>
          </div>
        )}

        {/* Rejection Info */}
        {quotation.status === QuotationStatus.REJECTED && quotation.rejection_reason && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-sm font-medium text-red-900 mb-1">Rejection Reason:</p>
            <p className="text-sm text-red-700">{quotation.rejection_reason}</p>
            {quotation.rejected_at && (
              <p className="text-xs text-red-600 mt-2">
                Rejected on {new Date(quotation.rejected_at).toLocaleString()}
              </p>
            )}
          </div>
        )}

        {/* Acceptance Info */}
        {quotation.status === QuotationStatus.ACCEPTED && quotation.accepted_at && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <p className="text-sm font-medium text-green-900">
              Accepted on {new Date(quotation.accepted_at).toLocaleString()}
            </p>
          </div>
        )}

        <div className="border-t pt-4">
          <p className="text-sm text-muted-foreground">
            Created: {new Date(quotation.created_at).toLocaleString()} |
            Last Updated: {new Date(quotation.updated_at).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Reject Dialog */}
      {showRejectDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold mb-4">Reject Quotation</h2>
            <textarea
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Enter rejection reason..."
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary min-h-[100px]"
            />
            <div className="flex gap-2 mt-4">
              <button
                onClick={handleReject}
                disabled={!rejectionReason.trim()}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                Reject
              </button>
              <button
                onClick={() => {
                  setShowRejectDialog(false);
                  setRejectionReason('');
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
