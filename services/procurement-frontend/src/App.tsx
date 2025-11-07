import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
// @ts-ignore - Module Federation remote import
import { AppLayout } from 'shared_components/AppLayout';
// @ts-ignore - Module Federation remote import
import { AuthProvider } from 'shared_components/AuthContext';

// Lazy load pages
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const PurchaseRequestList = lazy(() => import('@/pages/purchase-requests/PurchaseRequestList'));
const PurchaseRequestDetail = lazy(() => import('@/pages/purchase-requests/PurchaseRequestDetail'));
const PurchaseRequestForm = lazy(() => import('@/pages/purchase-requests/PurchaseRequestForm'));
const VendorList = lazy(() => import('@/pages/vendors/VendorList'));
const VendorDetail = lazy(() => import('@/pages/vendors/VendorDetail'));
const VendorForm = lazy(() => import('@/pages/vendors/VendorForm'));
const QuotationList = lazy(() => import('@/pages/quotations/QuotationList'));
const QuotationDetail = lazy(() => import('@/pages/quotations/QuotationDetail'));
const QuotationForm = lazy(() => import('@/pages/quotations/QuotationForm'));
const QuotationComparison = lazy(() => import('@/pages/quotations/QuotationComparison'));
const PurchaseOrderList = lazy(() => import('@/pages/purchase-orders/PurchaseOrderList'));
const PurchaseOrderDetail = lazy(() => import('@/pages/purchase-orders/PurchaseOrderDetail'));
const PurchaseOrderForm = lazy(() => import('@/pages/purchase-orders/PurchaseOrderForm'));

function App() {
  return (
    <AuthProvider apiBaseUrl="http://localhost:8000">
      <AppLayout currentService="procurement">
        <Suspense fallback={
          <div className="flex items-center justify-center h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        }>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />

            {/* Purchase Requests */}
            <Route path="/purchase-requests" element={<PurchaseRequestList />} />
            <Route path="/purchase-requests/create" element={<PurchaseRequestForm />} />
            <Route path="/purchase-requests/:id" element={<PurchaseRequestDetail />} />
            <Route path="/purchase-requests/:id/edit" element={<PurchaseRequestForm />} />

            {/* Vendors */}
            <Route path="/vendors" element={<VendorList />} />
            <Route path="/vendors/create" element={<VendorForm />} />
            <Route path="/vendors/:id" element={<VendorDetail />} />
            <Route path="/vendors/:id/edit" element={<VendorForm />} />

            {/* Quotations */}
            <Route path="/quotations" element={<QuotationList />} />
            <Route path="/quotations/create" element={<QuotationForm />} />
            <Route path="/quotations/:id" element={<QuotationDetail />} />
            <Route path="/quotations/:id/edit" element={<QuotationForm />} />
            <Route path="/purchase-requests/:prId/quotations/comparison" element={<QuotationComparison />} />

            {/* Purchase Orders */}
            <Route path="/purchase-orders" element={<PurchaseOrderList />} />
            <Route path="/purchase-orders/create" element={<PurchaseOrderForm />} />
            <Route path="/purchase-orders/:id" element={<PurchaseOrderDetail />} />
            <Route path="/purchase-orders/:id/edit" element={<PurchaseOrderForm />} />
          </Routes>
        </Suspense>
      </AppLayout>
    </AuthProvider>
  );
}

export default App;
