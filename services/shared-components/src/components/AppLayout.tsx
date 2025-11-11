import { AppSidebar } from "./AppSidebar";
import { useAuth } from "../contexts/AuthContext";

interface AppLayoutProps {
  children: React.ReactNode;
  currentService: 'dashboard' | 'auth' | 'assets' | 'procurement' | 'admin';
}

export function AppLayout({ children, currentService }: AppLayoutProps) {
  const { user, isLoading, logout } = useAuth();

  return (
    <div className="flex h-screen bg-background">
      <AppSidebar
        currentService={currentService}
        user={user}
        isLoading={isLoading}
        onLogout={logout}
      />

      <div className="flex-1 overflow-y-auto">{children}</div>
    </div>
  );
}
