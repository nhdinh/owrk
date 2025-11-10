import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  useFrameworkContract,
  useActivateContract,
  useSuspendContract,
  useTerminateContract,
  useDeleteContract,
} from '@/hooks/useFrameworkContracts';

const statusColors = {
  active: 'bg-green-100 text-green-800',
  expired: 'bg-gray-100 text-gray-800',
  terminated: 'bg-red-100 text-red-800',
};

const statusLabels = {
  active: 'Active',
  expired: 'Expired',
  terminated: 'Terminated',
};

export default function FrameworkContractDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showTerminateDialog, setShowTerminateDialog] = useState(false);
  const [terminationReason, setTerminationReason] = useState('');

  const { data: contract, isLoading, error } = useFrameworkContract(id!);
  const activateMutation = useActivateContract();
  const suspendMutation = useSuspendContract();
  const terminateMutation = useTerminateContract();
  const deleteMutation = useDeleteContract();

  const handleActivate = async () => {
    if (contract) {
      await activateMutation.mutateAsync(contract.id);
    }
  };

  const handleSuspend = async () => {
    if (contract && window.confirm('Are you sure you want to suspend this contract?')) {
      await suspendMutation.mutateAsync(contract.id);
    }
  };

  const handleTerminate = async () => {
    if (contract && terminationReason) {
      await terminateMutation.mutateAsync({
        id: contract.id,
        reason: terminationReason,
      });
      setShowTerminateDialog(false);
      setTerminationReason('');
    }
  };

  const handleDelete = async () => {
    if (contract && window.confirm('Are you sure you want to delete this contract? This action cannot be undone.')) {
      await deleteMutation.mutateAsync(contract.id);
      navigate('/framework-contracts');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !contract) {
    return (
      <div className="p-8">
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg">
          Error loading contract: {error instanceof Error ? error.message : 'Contract not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <Link to="/framework-contracts" className="text-primary hover:underline text-sm">
          ← Back to Framework Contracts
        </Link>
      </div>

      <div className="bg-card rounded-lg border border-border p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-3xl font-bold">{contract.contract_code}</h1>
            <p className="text-muted-foreground mt-1">{contract.contract_name}</p>
          </div>
          <div className="flex gap-2">
            {contract.status === 'active' && (
              <>
                <Link
                  to={`/framework-contracts/${contract.id}/edit`}
                  className="px-4 py-2 border border-input rounded-lg hover:bg-accent"
                >
                  Edit
                </Link>
                <button
                  onClick={handleSuspend}
                  className="px-4 py-2 border border-input rounded-lg hover:bg-accent"
                >
                  Suspend
                </button>
                <button
                  onClick={() => setShowTerminateDialog(true)}
                  className="px-4 py-2 border border-destructive text-destructive rounded-lg hover:bg-destructive/10"
                >
                  Terminate
                </button>
              </>
            )}
            {contract.status !== 'active' && contract.status !== 'terminated' && (
              <button
                onClick={handleActivate}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
              >
                Activate
              </button>
            )}
            <button
              onClick={handleDelete}
              className="px-4 py-2 border border-destructive text-destructive rounded-lg hover:bg-destructive/10"
            >
              Delete
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="p-4 bg-muted/50 rounded-lg">
            <p className="text-sm text-muted-foreground mb-1">Contract Value</p>
            <p className="text-2xl font-bold">${contract.contract_value.toLocaleString()}</p>
          </div>
          <div className="p-4 bg-muted/50 rounded-lg">
            <p className="text-sm text-muted-foreground mb-1">Contract Period</p>
            <p className="font-medium">{new Date(contract.start_date).toLocaleDateString()}</p>
            <p className="text-sm text-muted-foreground">to {new Date(contract.end_date).toLocaleDateString()}</p>
          </div>
          <div className="p-4 bg-muted/50 rounded-lg">
            <p className="text-sm text-muted-foreground mb-1">Status</p>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[contract.status]}`}>
              {statusLabels[contract.status]}
            </span>
          </div>
        </div>

        <div className="border-t border-border pt-6 space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Contract Code</p>
              <p className="font-medium">{contract.contract_code}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Contract Name</p>
              <p className="font-medium">{contract.contract_name}</p>
            </div>
          </div>

          <div className="border-t border-border pt-6">
            <p className="text-sm font-medium text-muted-foreground mb-3">Vendor</p>
            {contract.vendor ? (
              <div className="flex items-center justify-between bg-muted/30 p-4 rounded-lg">
                <div>
                  <p className="font-medium">{contract.vendor.vendor_name}</p>
                  <p className="text-sm text-muted-foreground">Code: {contract.vendor.vendor_code}</p>
                </div>
                <Link
                  to={`/vendors/${contract.vendor_id}`}
                  className="px-3 py-1 text-sm bg-secondary text-secondary-foreground rounded hover:bg-secondary/80"
                >
                  View Vendor
                </Link>
              </div>
            ) : (
              <p className="text-muted-foreground">Vendor information not available</p>
            )}
          </div>

          {contract.payment_terms && (
            <div className="border-t border-border pt-6">
              <p className="text-sm font-medium text-muted-foreground mb-2">Payment Terms</p>
              <p className="whitespace-pre-wrap">{contract.payment_terms}</p>
            </div>
          )}

          {contract.delivery_terms && (
            <div className="border-t border-border pt-6">
              <p className="text-sm font-medium text-muted-foreground mb-2">Delivery Terms</p>
              <p className="whitespace-pre-wrap">{contract.delivery_terms}</p>
            </div>
          )}

          {contract.terms_and_conditions && (
            <div className="border-t border-border pt-6">
              <p className="text-sm font-medium text-muted-foreground mb-2">Terms and Conditions</p>
              <p className="whitespace-pre-wrap">{contract.terms_and_conditions}</p>
            </div>
          )}

          {contract.contract_file_url && (
            <div className="border-t border-border pt-6">
              <p className="text-sm font-medium text-muted-foreground mb-2">Contract Document</p>
              <a
                href={contract.contract_file_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                View Contract Document
              </a>
            </div>
          )}

          <div className="border-t border-border pt-6">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground mb-1">Created</p>
                <p>{new Date(contract.created_at).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">Last Updated</p>
                <p>{new Date(contract.updated_at).toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Terminate Dialog */}
      {showTerminateDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-card rounded-lg p-6 max-w-md w-full border border-border">
            <h2 className="text-xl font-bold mb-2">Terminate Contract</h2>
            <p className="text-muted-foreground mb-4">
              Please provide a reason for terminating this contract. This action is permanent.
            </p>
            <textarea
              placeholder="Enter termination reason..."
              value={terminationReason}
              onChange={(e) => setTerminationReason(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-input rounded-lg bg-background mb-4"
            />
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowTerminateDialog(false)}
                className="px-4 py-2 border border-input rounded-lg hover:bg-accent"
              >
                Cancel
              </button>
              <button
                onClick={handleTerminate}
                disabled={!terminationReason}
                className="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Terminate Contract
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
