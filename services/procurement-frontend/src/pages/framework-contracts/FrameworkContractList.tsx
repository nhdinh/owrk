import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useFrameworkContracts, useDeleteContract } from '@/hooks/useFrameworkContracts';

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

export default function FrameworkContractList() {
  const [filters, setFilters] = useState({
    skip: 0,
    limit: 20,
    status: undefined as string | undefined,
    vendor_id: undefined as number | undefined,
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const { data, isLoading, error } = useFrameworkContracts(filters);
  const deleteMutation = useDeleteContract();

  const handleDelete = async () => {
    if (deleteId) {
      await deleteMutation.mutateAsync(deleteId);
      setDeleteId(null);
    }
  };

  const filteredContracts = data?.data?.filter((contract) => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      contract.contract_code.toLowerCase().includes(search) ||
      contract.contract_name.toLowerCase().includes(search) ||
      contract.vendor?.vendor_name?.toLowerCase().includes(search)
    );
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg">
          Error loading contracts: {(error as Error).message}
        </div>
      </div>
    );
  }

  const totalPages = data ? Math.ceil(data.total / filters.limit) : 0;
  const currentPage = Math.floor(filters.skip / filters.limit) + 1;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Framework Contracts</h1>
          <p className="text-muted-foreground mt-1">Manage long-term supplier agreements</p>
        </div>
        <Link
          to="/framework-contracts/create"
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          New Contract
        </Link>
      </div>

      {/* Filters */}
      <div className="mb-6 flex gap-4">
        <input
          type="text"
          placeholder="Search by code, name, or vendor..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-4 py-2 border border-input rounded-lg bg-background"
        />
        <select
          value={filters.status || ''}
          onChange={(e) => setFilters({ ...filters, status: e.target.value || undefined, skip: 0 })}
          className="px-4 py-2 border border-input rounded-lg bg-background"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="expired">Expired</option>
          <option value="terminated">Terminated</option>
        </select>
      </div>

      {/* Contracts Table */}
      {filteredContracts && filteredContracts.length > 0 ? (
        <>
          <div className="bg-card rounded-lg border border-border overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Contract Code</th>
                  <th className="text-left p-4 font-medium">Contract Name</th>
                  <th className="text-left p-4 font-medium">Vendor</th>
                  <th className="text-left p-4 font-medium">Value</th>
                  <th className="text-left p-4 font-medium">Period</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredContracts.map((contract) => (
                  <tr key={contract.id} className="border-t border-border hover:bg-muted/50">
                    <td className="p-4 font-medium">{contract.contract_code}</td>
                    <td className="p-4">{contract.contract_name}</td>
                    <td className="p-4">{contract.vendor?.vendor_name || 'N/A'}</td>
                    <td className="p-4">${contract.contract_value.toLocaleString()}</td>
                    <td className="p-4">
                      <div className="text-sm">
                        <div>{new Date(contract.start_date).toLocaleDateString()}</div>
                        <div className="text-muted-foreground">
                          to {new Date(contract.end_date).toLocaleDateString()}
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[contract.status]}`}>
                        {statusLabels[contract.status]}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex justify-end gap-2">
                        <Link
                          to={`/framework-contracts/${contract.id}`}
                          className="px-3 py-1 text-sm bg-secondary text-secondary-foreground rounded hover:bg-secondary/80"
                        >
                          View
                        </Link>
                        {contract.status === 'active' && (
                          <Link
                            to={`/framework-contracts/${contract.id}/edit`}
                            className="px-3 py-1 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90"
                          >
                            Edit
                          </Link>
                        )}
                        <button
                          onClick={() => setDeleteId(contract.id)}
                          className="px-3 py-1 text-sm bg-destructive text-destructive-foreground rounded hover:bg-destructive/90"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-4 flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Showing {filters.skip + 1} to {Math.min(filters.skip + filters.limit, data?.total || 0)} of {data?.total || 0} contracts
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilters({ ...filters, skip: Math.max(0, filters.skip - filters.limit) })}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-input rounded-lg bg-background hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setFilters({ ...filters, skip: filters.skip + filters.limit })}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border border-input rounded-lg bg-background hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12 bg-card rounded-lg border border-border">
          <p className="text-muted-foreground mb-4">No framework contracts found</p>
          <Link
            to="/framework-contracts/create"
            className="inline-block px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
          >
            Create First Contract
          </Link>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {deleteId !== null && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-card rounded-lg p-6 max-w-md w-full border border-border">
            <h2 className="text-xl font-bold mb-2">Delete Contract</h2>
            <p className="text-muted-foreground mb-6">
              Are you sure you want to delete this contract? This action will terminate the contract permanently.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteId(null)}
                className="px-4 py-2 border border-input rounded-lg hover:bg-accent"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
