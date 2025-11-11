import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useVendors } from '@/hooks/useVendors';
import { VendorStatus } from '@/types';

export default function VendorList() {
  const [filters, setFilters] = useState({
    skip: 0,
    limit: 20,
    search: '',
    status: undefined as VendorStatus | undefined,
  });

  const { data, isLoading, error } = useVendors(filters);

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
          Error loading vendors: {(error as Error).message}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Vendors</h1>
          <p className="text-muted-foreground mt-1">Manage supplier information</p>
        </div>
        <Link
          to="/vendors/create"
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          Add Vendor
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-card rounded-lg border p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Search vendors..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value, skip: 0 })}
            className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <select
            value={filters.status || ''}
            onChange={(e) => setFilters({ ...filters, status: e.target.value as VendorStatus || undefined, skip: 0 })}
            className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">All Status</option>
            {Object.values(VendorStatus).map((status) => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
          <button
            onClick={() => setFilters({ skip: 0, limit: 20, search: '', status: undefined })}
            className="px-4 py-2 border rounded-lg hover:bg-muted transition-colors"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-card rounded-lg border overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium">Vendor Code</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Contact Person</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Email</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Phone</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Rating</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {data?.items?.map((vendor) => (
              <tr key={vendor.id} className="hover:bg-muted/50">
                <td className="px-4 py-3">
                  <Link to={`/vendors/${vendor.id}`} className="text-primary hover:underline font-medium">
                    {vendor.vendor_code}
                  </Link>
                </td>
                <td className="px-4 py-3">{vendor.name}</td>
                <td className="px-4 py-3">{vendor.contact_person || '-'}</td>
                <td className="px-4 py-3">{vendor.email || '-'}</td>
                <td className="px-4 py-3">{vendor.phone || '-'}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${vendor.status === VendorStatus.ACTIVE ? 'bg-green-100 text-green-700' :
                    vendor.status === VendorStatus.BLACKLISTED ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                    {vendor.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {vendor.rating ? (
                    <div className="flex items-center gap-1">
                      <span className="text-yellow-500">★</span>
                      <span>{vendor.rating.toFixed(1)}</span>
                    </div>
                  ) : '-'}
                </td>
                <td className="px-4 py-3">
                  <Link
                    to={`/vendors/${vendor.id}`}
                    className="text-primary hover:underline text-sm"
                  >
                    View Details
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {data?.items?.length === 0 && (
          <div className="py-12 text-center text-muted-foreground">
            No vendors found
          </div>
        )}

        {/* Pagination */}
        {data && data.total > filters.limit && (
          <div className="px-4 py-3 border-t flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Showing {filters.skip + 1} - {Math.min(filters.skip + filters.limit, data.total)} of {data.total}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setFilters({ ...filters, skip: Math.max(0, filters.skip - filters.limit) })}
                disabled={filters.skip === 0}
                className="px-3 py-1 border rounded-lg hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                Previous
              </button>
              <button
                onClick={() => setFilters({ ...filters, skip: filters.skip + filters.limit })}
                disabled={filters.skip + filters.limit >= data.total}
                className="px-3 py-1 border rounded-lg hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
