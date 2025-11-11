import { Link } from 'react-router-dom';
import { usePurchaseRequests } from '@/hooks/usePurchaseRequests';
import { useVendors } from '@/hooks/useVendors';
import { useQuotations } from '@/hooks/useQuotations';
import { usePurchaseOrders } from '@/hooks/usePurchaseOrders';
import { PurchaseRequestStatus } from '@/types';

export default function Dashboard() {
  const { data: purchaseRequests } = usePurchaseRequests({ limit: 5 });
  const { data: vendors } = useVendors({ limit: 5 });
  const { data: quotations } = useQuotations({ limit: 5 });
  const { data: purchaseOrders } = usePurchaseOrders({ limit: 5 });

  const pendingPRs = purchaseRequests?.items?.filter(
    (pr) => pr.status === PurchaseRequestStatus.PENDING
  ).length || 0;

  const approvedPRs = purchaseRequests?.items?.filter(
    (pr) => pr.status === PurchaseRequestStatus.APPROVED
  ).length || 0;

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-foreground">Procurement Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Manage purchase requests, vendors, quotations, and purchase orders
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-card rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Purchase Requests</p>
              <p className="text-3xl font-bold text-foreground mt-2">{purchaseRequests?.total || 0}</p>
              <p className="text-sm text-yellow-600 mt-1">{pendingPRs} pending approval</p>
            </div>
            <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
          <Link to="/purchase-requests" className="text-sm text-primary hover:underline mt-4 block">
            View all →
          </Link>
        </div>

        <div className="bg-card rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Vendors</p>
              <p className="text-3xl font-bold text-foreground mt-2">{vendors?.total || 0}</p>
              <p className="text-sm text-green-600 mt-1">Active suppliers</p>
            </div>
            <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
          <Link to="/vendors" className="text-sm text-primary hover:underline mt-4 block">
            View all →
          </Link>
        </div>

        <div className="bg-card rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Quotations</p>
              <p className="text-3xl font-bold text-foreground mt-2">{quotations?.total || 0}</p>
              <p className="text-sm text-purple-600 mt-1">Received quotes</p>
            </div>
            <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          <Link to="/quotations" className="text-sm text-primary hover:underline mt-4 block">
            View all →
          </Link>
        </div>

        <div className="bg-card rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Purchase Orders</p>
              <p className="text-3xl font-bold text-foreground mt-2">{purchaseOrders?.total || 0}</p>
              <p className="text-sm text-orange-600 mt-1">Active orders</p>
            </div>
            <div className="h-12 w-12 bg-orange-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
            </div>
          </div>
          <Link to="/purchase-orders" className="text-sm text-primary hover:underline mt-4 block">
            View all →
          </Link>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card rounded-lg border p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              to="/purchase-requests/create"
              className="block p-4 rounded-lg border border-dashed border-primary bg-primary/5 hover:bg-primary/10 transition-colors"
            >
              <p className="font-medium text-primary">Create Purchase Request</p>
              <p className="text-sm text-muted-foreground mt-1">Start a new procurement request</p>
            </Link>
            <Link
              to="/vendors/create"
              className="block p-4 rounded-lg border border-dashed hover:bg-muted/50 transition-colors"
            >
              <p className="font-medium">Add New Vendor</p>
              <p className="text-sm text-muted-foreground mt-1">Register a new supplier</p>
            </Link>
            <Link
              to="/quotations/create"
              className="block p-4 rounded-lg border border-dashed hover:bg-muted/50 transition-colors"
            >
              <p className="font-medium">Create Quotation</p>
              <p className="text-sm text-muted-foreground mt-1">Add vendor quotation</p>
            </Link>
          </div>
        </div>

        <div className="bg-card rounded-lg border p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {purchaseRequests?.items?.slice(0, 5).map((pr) => (
              <div key={pr.id} className="flex items-start gap-3 pb-3 border-b last:border-0">
                <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <svg className="h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <Link to={`/purchase-requests/${pr.id}`} className="font-medium hover:text-primary">
                    {pr.title}
                  </Link>
                  <p className="text-sm text-muted-foreground truncate">{pr.request_code}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(pr.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  pr.status === PurchaseRequestStatus.APPROVED
                    ? 'bg-green-100 text-green-700'
                    : pr.status === PurchaseRequestStatus.PENDING
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {pr.status}
                </span>
              </div>
            ))}
            {(!purchaseRequests || purchaseRequests.items?.length === 0) && (
              <p className="text-sm text-muted-foreground text-center py-4">No recent activity</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
