import { useQuery } from "@tanstack/react-query";
import { dashboardAPI } from "@/lib/dashboard-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
// @ts-ignore - Module Federation remote import
import { AppSidebar } from "shared_components/AppSidebar";
import {
  Users,
  Package,
  Activity,
  Shield,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  XCircle,
  Gauge,
} from "lucide-react";

export default function Dashboard() {
  const { data: overview, isLoading } = useQuery({
    queryKey: ["dashboardOverview"],
    queryFn: () => dashboardAPI.getOverview(),
    refetchInterval: 30000,
  });

  const { data: _ } = useQuery({
    queryKey: ["dashboardRegister"],
    queryFn: () => dashboardAPI.registerService(),
    refetchInterval: 6000,
  });

  const { data: health } = useQuery({
    queryKey: ["systemHealth"],
    queryFn: () => dashboardAPI.getHealth(),
    refetchInterval: 60000,
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="h-4 w-4 text-green-300" />;
      case "degraded":
        return <AlertCircle className="h-4 w-4 text-yellow-300" />;
      case "down":
        return <XCircle className="h-4 w-4 text-red-300" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-300" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-green-600";
      case "degraded":
        return "text-yellow-600";
      case "down":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  return (
    <div className="flex h-screen bg-background">
      <AppSidebar currentService="dashboard" />

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="border-b bg-card">
          <div className="px-4 py-4 lg:px-8">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Gauge className="h-6 w-6" />
              System Dashboard
            </h1>
            <p className="text-sm text-muted-foreground">
              Centralized monitoring and statistics
            </p>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-4 py-8 lg:px-8">
          {/* System Health Status */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">System Health</h2>
            <div className="grid gap-4 md:grid-cols-4">
              {health?.services.map((service) => (
                <Card key={service.service}>
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium">
                      {service.service}
                    </CardTitle>
                    {getStatusIcon(service.status)}
                  </CardHeader>
                  <CardContent>
                    <div
                      className={`text-xl font-bold ${getStatusColor(
                        service.status
                      )}`}
                    >
                      {service.status.toUpperCase()}
                    </div>
                    {service.response_time_ms && (
                      <p className="text-xs text-muted-foreground">
                        {service.response_time_ms.toFixed(0)}ms response time
                      </p>
                    )}
                    {service.last_check && (
                      <p className="text-xs text-muted-foreground">
                        Last check: {new Date(service.last_check).toString()}
                      </p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* User Statistics */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">User Statistics</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Total Users
                  </CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className="h-8 w-16" />
                  ) : (
                    <div className="text-2xl font-bold">
                      {overview?.system_stats.total_users || 0}
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground">
                    Active system users
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Active Users
                  </CardTitle>
                  <Activity className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className="h-8 w-16" />
                  ) : (
                    <div className="text-2xl font-bold text-green-600">
                      {overview?.system_stats.active_users || 0}
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {overview?.system_stats.inactive_users || 0} inactive
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Roles</CardTitle>
                  <Shield className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className="h-8 w-16" />
                  ) : (
                    <div className="text-2xl font-bold">
                      {overview?.system_stats.total_roles || 0}
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground">Defined roles</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    MFA Enabled
                  </CardTitle>
                  <Shield className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className="h-8 w-16" />
                  ) : (
                    <div className="text-2xl font-bold text-blue-600">
                      {overview?.system_stats.users_with_mfa || 0}
                    </div>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {overview?.system_stats.total_users
                      ? `${Math.round(
                          (overview.system_stats.users_with_mfa /
                            overview.system_stats.total_users) *
                            100
                        )}% of users`
                      : "No users"}
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Asset Statistics */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Asset Statistics</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-5">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Total Assets
                  </CardTitle>
                  <Package className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className="h-8 w-16" />
                  ) : (
                    <div className="text-2xl font-bold">
                      {overview?.asset_stats.total_assets || 0}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Available
                  </CardTitle>
                  <TrendingUp className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className="h-8 w-16" />
                  ) : (
                    <div className="text-2xl font-bold text-green-600">
                      {overview?.asset_stats.available_assets || 0}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Assigned
                  </CardTitle>
                  <Activity className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className="h-8 w-16" />
                  ) : (
                    <div className="text-2xl font-bold text-blue-600">
                      {overview?.asset_stats.assigned_assets || 0}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    In Maintenance
                  </CardTitle>
                  <AlertCircle className="h-4 w-4 text-yellow-600" />
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className="h-8 w-16" />
                  ) : (
                    <div className="text-2xl font-bold text-yellow-600">
                      {overview?.asset_stats.in_maintenance_assets || 0}
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Disposed
                  </CardTitle>
                  <XCircle className="h-4 w-4 text-gray-600" />
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <Skeleton className="h-8 w-16" />
                  ) : (
                    <div className="text-2xl font-bold text-gray-600">
                      {overview?.asset_stats.disposed_assets || 0}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
