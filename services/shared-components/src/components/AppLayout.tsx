import { AppSidebar } from './AppSidebar';

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="flex h-screen bg-background">
      <AppSidebar currentService="assets" />

      <div className="flex-1 overflow-y-auto">
        {children}
      </div>
    </div>
  );
}
