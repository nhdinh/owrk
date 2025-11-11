import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuotations } from '@/hooks/useQuotations';
import { QuotationStatus } from '@/types';

export default function QuotationList() {
  const [filters, setFilters] = useState({
    skip: 0,
    limit: 20,
    status: undefined as QuotationStatus | undefined,
    date_from: '',
    date_to: '',
  });

  const { data, isLoading, error } = useQuotations(filters);

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
          Error loading quotations: {(error as Error).message}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Quotations</h1>
          <p className="text-muted-foreground mt-1">Manage vendor quotations for purchase requests</p>
        </div>
        <Link
          to="/quotations/create"
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          Create Quotation
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-card rounded-lg border p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={filters.status || ''}
            onChange={(e) => setFilters({ ...filters, status: e.target.value as QuotationStatus || undefined, skip: 0 })}
            className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">All Status</option>
            {Object.values(QuotationStatus).map((status) => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
          <input
            type="date"
            value={filters.date_from}
            onChange={(e) => setFilters({ ...filters, date_from: e.target.value, skip: 0 })}
            placeholder="From Date"
            className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <input
            type="date"
            value={filters.date_to}
            onChange={(e) => setFilters({ ...filters, date_to: e.target.value, skip: 0 })}
            placeholder="To Date"
            className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            onClick={() => setFilters({ skip: 0, limit: 20, status: undefined, date_from: '', date_to: '' })}
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
              <th className="px-4 py-3 text-left text-sm font-medium">Quotation Code</th>
              <th className="px-4 py-3 text-left text-sm font-medium">PR Code</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Vendor</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Date</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Valid Until</th>
              <th className="px-4 py-3 text-right text-sm font-medium">Final Amount</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
              <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {data?.items?.map((quotation) => (
              <tr key={quotation.id} className="hover:bg-muted/50">
                <td className="px-4 py-3">
                  <Link to={`/quotations/${quotation.id}`} className="text-primary hover:underline font-medium">
                    {quotation.quotation_code}
                  </Link>
                </td>
                <td className="px-4 py-3">
                  {quotation.purchase_request ? (
                    <Link
                      to={`/purchase-requests/${quotation.purchase_request.id}`}
                      className="text-primary hover:underline"
                    >
                      {quotation.purchase_request.request_code}
                    </Link>
                  ) : '-'}
                </td>
                <td className="px-4 py-3">{quotation.vendor?.name || '-'}</td>
                <td className="px-4 py-3">{new Date(quotation.quotation_date).toLocaleDateString()}</td>
                <td className="px-4 py-3">
                  {quotation.valid_until ? new Date(quotation.valid_until).toLocaleDateString() : '-'}
                </td>
                <td className="px-4 py-3 text-right font-medium">${quotation.final_amount.toFixed(2)}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${quotation.status === QuotationStatus.ACCEPTED ? 'bg-green-100 text-green-700' :
                    quotation.status === QuotationStatus.REJECTED ? 'bg-red-100 text-red-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                    {quotation.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <Link
                    to={`/quotations/${quotation.id}`}
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
            No quotations found
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
