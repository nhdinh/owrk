import { AppSidebar, AppSidebarProps } from "./AppSidebar";

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout(
  { currentService }: AppSidebarProps,
  { children }: AppLayoutProps
) {
  return (
    <div className="flex h-screen bg-background">
      <AppSidebar currentService={currentService} />

      <div className="flex-1 overflow-y-auto">{children}</div>
    </div>
  );
}
