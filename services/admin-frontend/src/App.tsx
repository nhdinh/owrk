import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
// @ts-ignore - Module Federation remote import
import { AuthProvider, useAuth } from "shared_components/AuthContext";
import Dashboard from './pages/Dashboard';
import TrashPage from './pages/TrashPage';
import SettingsPage from './pages/SettingsPage';

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  return <>{children}</>;
}

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/trash"
        element={
          <ProtectedRoute>
            <TrashPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

const App = () => (
  <BrowserRouter basename="/admin">
    <AuthProvider apiBaseUrl="http://localhost:8000">
      <AppRoutes />
    </AuthProvider>
  </BrowserRouter>
);

export default App;
