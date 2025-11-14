// @ts-expect-error - Module Federation remote import
import { Toaster } from "shared_components/ui/toaster";
// @ts-expect-error - Module Federation remote import
import { Toaster as Sonner } from "shared_components/ui/sonner";
// @ts-expect-error - Module Federation remote import
import { TooltipProvider } from "shared_components/ui/tooltip";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
// @ts-ignore - Module Federation remote import
import { AuthProvider, useAuth } from "shared_components/AuthContext";
import Dashboard from "./pages/Dashboard";
import "./index.css";
import React from "react";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
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
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      {/* catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter basename="/dashboard">
          <AuthProvider apiBaseUrl="http://localhost:8000">
            <AppRoutes />
          </AuthProvider>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
