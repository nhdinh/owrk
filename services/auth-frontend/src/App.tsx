// @ts-expect-error - Module Federation remote import
import { Toaster } from "shared_components/ui/toaster";
// @ts-expect-error - Module Federation remote import
import { Toaster as Sonner } from "shared_components/ui/sonner";
// @ts-expect-error - Module Federation remote import
import { TooltipProvider } from "shared_components/ui/tooltip";
// @ts-expect-error - Module Federation remote import
import { AuthProvider, useAuth } from "shared_components/AuthContext";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// Pages
import Login from "./pages/Login";
import VerifyOTP from "./pages/VerifyOTP";
import ForgotPassword from "./pages/ForgotPassword";
import Users from "./pages/Users";
import UserDetail from "./pages/UserDetail";
import UserEdit from "./pages/UserEdit";
import Roles from "./pages/Roles";
import RoleDetail from "./pages/RoleDetail";
import RoleEdit from "./pages/RoleEdit";
import RoleCreate from "./pages/RoleCreate";
import Profile from "./pages/Profile";

const queryClient = new QueryClient();

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Public Route Component (redirect if already logged in)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route path="/verify-otp" element={<VerifyOTP />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />

      {/* Protected Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Users />
          </ProtectedRoute>
        }
      />
      <Route
        path="/users"
        element={
          <ProtectedRoute>
            <Users />
          </ProtectedRoute>
        }
      />
      <Route
        path="/users/:id"
        element={
          <ProtectedRoute>
            <UserDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/users/:id/edit"
        element={
          <ProtectedRoute>
            <UserEdit />
          </ProtectedRoute>
        }
      />
      <Route
        path="/roles"
        element={
          <ProtectedRoute>
            <Roles />
          </ProtectedRoute>
        }
      />
      <Route
        path="/roles/create"
        element={
          <ProtectedRoute>
            <RoleCreate />
          </ProtectedRoute>
        }
      />
      <Route
        path="/roles/:id"
        element={
          <ProtectedRoute>
            <RoleDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/roles/:id/edit"
        element={
          <ProtectedRoute>
            <RoleEdit />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        }
      />

      {/* Catch all - redirect to login */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter basename="/auth">
        <AuthProvider apiBaseUrl="http://localhost:8000">
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
