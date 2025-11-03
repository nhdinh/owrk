import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
// @ts-ignore - Module Federation remote import
import { AuthProvider, useAuth } from "shared_components/AuthContext";

// Pages
import Assets from "./pages/Assets";
import AssetDetail from "./pages/AssetDetail";
import AssetForm from "./pages/AssetForm";
import Categories from "./pages/Categories";
import Assignments from "./pages/Assignments";
import Maintenance from "./pages/Maintenance";

const queryClient = new QueryClient();

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!isAuthenticated) {
    // Redirect to auth frontend if not authenticated
    window.location.href = "/auth/login";
    return null;
  }

  return <>{children}</>;
}

const AppRoutes = () => {
  return (
    <Routes>
      {/* Protected Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Assets />
          </ProtectedRoute>
        }
      />
      <Route
        path="/assets"
        element={
          <ProtectedRoute>
            <Assets />
          </ProtectedRoute>
        }
      />
      <Route
        path="/assets/new"
        element={
          <ProtectedRoute>
            <AssetForm />
          </ProtectedRoute>
        }
      />
      <Route
        path="/assets/:id"
        element={
          <ProtectedRoute>
            <AssetDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/assets/:id/edit"
        element={
          <ProtectedRoute>
            <AssetForm />
          </ProtectedRoute>
        }
      />
      <Route
        path="/categories"
        element={
          <ProtectedRoute>
            <Categories />
          </ProtectedRoute>
        }
      />
      <Route
        path="/assignments"
        element={
          <ProtectedRoute>
            <Assignments />
          </ProtectedRoute>
        }
      />
      <Route
        path="/maintenance"
        element={
          <ProtectedRoute>
            <Maintenance />
          </ProtectedRoute>
        }
      />

      {/* Catch all - redirect to assets */}
      <Route path="*" element={<Navigate to="/assets" replace />} />
    </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter basename="/assets">
        <AuthProvider apiBaseUrl="http://localhost:8000">
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
