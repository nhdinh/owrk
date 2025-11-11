import { useParams, Link, useNavigate } from 'react-router-dom';
import { usePurchaseRequest, useApprovePurchaseRequest, useRejectPurchaseRequest, useDeletePurchaseRequest } from '@/hooks/usePurchaseRequests';
import { PurchaseRequestStatus } from '@/types';
import { useState } from 'react';

export default function PurchaseRequestDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: pr, isLoading, error } = usePurchaseRequest(id!);
  const approveMutation = useApprovePurchaseRequest();
  const rejectMutation = useRejectPurchaseRequest();
  const deleteMutation = useDeletePurchaseRequest();

  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !pr) {
    return (
      <div className="p-8">
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg">
          Error loading purchase request
        </div>
      </div>
    );
  }

  const handleApprove = async (level: number) => {
    try {
      await approveMutation.mutateAsync({ id: pr.id, level });
    } catch (error) {
      console.error('Failed to approve:', error);
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) return;
    try {
      await rejectMutation.mutateAsync({ id: pr.id, reason: rejectionReason });
      setShowRejectDialog(false);
      setRejectionReason('');
    } catch (error) {
      console.error('Failed to reject:', error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this purchase request?')) {
      try {
        await deleteMutation.mutateAsync(pr.id);
        navigate('/purchase-requests');
      } catch (error) {
        console.error('Failed to delete:', error);
      }
    }
  };

  return (
    <div className="p-8">
      <div className="mb-6">
        <Link to="/purchase-requests" className="text-primary hover:underline text-sm">
          ← Back to Purchase Requests
        </Link>
      </div>

      <div className="bg-card rounded-lg border p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl font-bold">{pr.title}</h1>
            <p className="text-muted-foreground mt-1">{pr.request_code}</p>
          </div>
          <div className="flex gap-2">
            {pr.status === PurchaseRequestStatus.DRAFT && (
              <Link
                to={`/purchase-requests/${pr.id}/edit`}
                className="px-4 py-2 border rounded-lg hover:bg-muted"
              >
                Edit
              </Link>
            )}
            {pr.status === PurchaseRequestStatus.PENDING && (
              <>
                <button
                  onClick={() => handleApprove(1)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Approve
                </button>
                <button
                  onClick={() => setShowRejectDialog(true)}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Reject
                </button>
              </>
            )}
            {pr.status === PurchaseRequestStatus.DRAFT && (
              <button
                onClick={handleDelete}
                className="px-4 py-2 border border-destructive text-destructive rounded-lg hover:bg-destructive/10"
              >
                Delete
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <p className="text-sm text-muted-foreground">Department</p>
            <p className="font-medium">{pr.department?.name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Requester</p>
            <p className="font-medium">{pr.requester?.full_name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Priority</p>
            <p className="font-medium">{pr.priority}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Status</p>
            <span className={`px-2 py-1 text-xs rounded-full ${
              pr.status === PurchaseRequestStatus.APPROVED ? 'bg-green-100 text-green-700' :
              pr.status === PurchaseRequestStatus.REJECTED ? 'bg-red-100 text-red-700' :
              'bg-yellow-100 text-yellow-700'
            }`}>
              {pr.status}
            </span>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Request Date</p>
            <p className="font-medium">{new Date(pr.request_date).toLocaleDateString()}</p>
          </div>
          {pr.required_date && (
            <div>
              <p className="text-sm text-muted-foreground">Required Date</p>
              <p className="font-medium">{new Date(pr.required_date).toLocaleDateString()}</p>
            </div>
          )}
        </div>

        {pr.description && (
          <div className="mb-6">
            <p className="text-sm text-muted-foreground mb-2">Description</p>
            <p>{pr.description}</p>
          </div>
        )}

        {pr.justification && (
          <div className="mb-6">
            <p className="text-sm text-muted-foreground mb-2">Justification</p>
            <p>{pr.justification}</p>
          </div>
        )}

        <div>
          <h2 className="text-xl font-semibold mb-4">Items</h2>
          <table className="w-full border rounded-lg">
            <thead className="bg-muted">
              <tr>
                <th className="px-4 py-2 text-left">Item Name</th>
                <th className="px-4 py-2 text-left">Description</th>
                <th className="px-4 py-2 text-right">Quantity</th>
                <th className="px-4 py-2 text-left">Unit</th>
                <th className="px-4 py-2 text-right">Estimated Price</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {pr.items.map((item, index) => (
                <tr key={index}>
                  <td className="px-4 py-2">{item.item_name}</td>
                  <td className="px-4 py-2">{item.description || '-'}</td>
                  <td className="px-4 py-2 text-right">{item.quantity}</td>
                  <td className="px-4 py-2">{item.unit}</td>
                  <td className="px-4 py-2 text-right">
                    {item.estimated_total_price ? `$${item.estimated_total_price.toFixed(2)}` : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Reject Dialog */}
      {showRejectDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold mb-4">Reject Purchase Request</h2>
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
