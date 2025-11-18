import { useEffect, useState } from "react";
import {
  monitoringAPI,
  type DashboardData,
  type ServiceMetrics,
} from "@/lib/dashboard-api";
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import {
  Activity,
  Server,
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle2,
  RefreshCcw,
} from "lucide-react";
// @ts-expect-error - Module Federation remote import
import { AppLayout } from "shared_components/AppLayout";
// @ts-expect-error - Module Federation remote import
import { Card, CardContent, CardHeader, CardTitle } from "shared_components/ui/card";
// @ts-expect-error - Module Federation remote import
import { Button } from "shared_components/ui/button";
// @ts-expect-error - Module Federation remote import
import { Badge } from "shared_components/ui/badge";

export default function Status() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timePeriod, setTimePeriod] = useState(24);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [timePeriod]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await monitoringAPI.getDashboard(timePeriod);
      setDashboardData(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch data");
    } finally {
      setLoading(false);
    }
  };

  if (loading && !dashboardData) {
    return (
      <AppLayout currentService="dashboard">
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
          <div className="flex flex-col items-center gap-4">
            <RefreshCcw className="h-8 w-8 animate-spin text-muted-foreground" />
            <p className="text-lg text-muted-foreground">Loading monitoring data...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (error) {
    return (
      <AppLayout currentService="dashboard">
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
          <div className="flex flex-col items-center gap-4">
            <AlertCircle className="h-12 w-12 text-destructive" />
            <p className="text-lg text-destructive">Error: {error}</p>
            <Button onClick={fetchDashboardData} variant="outline">
              <RefreshCcw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (!dashboardData) {
    return null;
  }

  const { statistics, services } = dashboardData;

  return (
    <AppLayout currentService="dashboard">
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="px-4 py-4 lg:px-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <Activity className="h-6 w-6" />
                  Service Registry Monitoring
                </h1>
                <p className="text-sm text-muted-foreground">
                  Real-time service health and performance metrics
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchDashboardData}
                disabled={loading}
              >
                <RefreshCcw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-4 py-8 lg:px-8">
          {/* Time Period Selector */}
          <div className="mb-6 flex flex-wrap gap-2">
            <span className="text-sm text-muted-foreground flex items-center mr-2">
              Time Period:
            </span>
            {[1, 6, 12, 24, 48, 72].map((hours) => (
              <Button
                key={hours}
                variant={timePeriod === hours ? "default" : "outline"}
                size="sm"
                onClick={() => setTimePeriod(hours)}
              >
                {hours}h
              </Button>
            ))}
          </div>

          {/* Statistics Cards */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Overview</h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <StatCard
                icon={<Server className="h-4 w-4" />}
                title="Total Services"
                value={statistics.total_services}
                color="blue"
                iconColor="text-blue-600"
              />
              <StatCard
                icon={<CheckCircle2 className="h-4 w-4" />}
                title="Healthy Services"
                value={statistics.healthy_services}
                color="green"
                iconColor="text-green-600"
              />
              <StatCard
                icon={<AlertCircle className="h-4 w-4" />}
                title="Down Services"
                value={statistics.down_services}
                color="red"
                iconColor="text-red-600"
              />
              <StatCard
                icon={<Clock className="h-4 w-4" />}
                title="Avg Response Time"
                value={`${statistics.average_response_time.toFixed(1)}ms`}
                color="purple"
                iconColor="text-purple-600"
              />
            </div>
          </div>

          {/* Services Grid */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Service Details</h2>
            <div className="grid gap-6 md:grid-cols-2">
              {services.map((service) => (
                <ServiceCard key={service.name} service={service} />
              ))}
            </div>
          </div>

          {/* Charts */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Performance Metrics</h2>
            <div className="grid gap-6 lg:grid-cols-2">
              {/* Response Time Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-blue-600" />
                    Response Time Comparison
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={services}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis
                        dataKey="name"
                        className="text-xs"
                        tick={{ fill: 'hsl(var(--muted-foreground))' }}
                      />
                      <YAxis
                        className="text-xs"
                        tick={{ fill: 'hsl(var(--muted-foreground))' }}
                        label={{
                          value: "ms",
                          angle: -90,
                          position: "insideLeft",
                          style: { fill: 'hsl(var(--muted-foreground))' }
                        }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "hsl(var(--popover))",
                          border: "1px solid hsl(var(--border))",
                          borderRadius: "0.5rem",
                        }}
                      />
                      <Legend />
                      <Bar
                        dataKey="current_response_time"
                        fill="hsl(var(--primary))"
                        name="Response Time (ms)"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Uptime Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-green-600" />
                    Service Uptime ({timePeriod}h)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={services}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis
                        dataKey="name"
                        className="text-xs"
                        tick={{ fill: 'hsl(var(--muted-foreground))' }}
                      />
                      <YAxis
                        className="text-xs"
                        tick={{ fill: 'hsl(var(--muted-foreground))' }}
                        domain={[0, 100]}
                        label={{
                          value: "%",
                          angle: -90,
                          position: "insideLeft",
                          style: { fill: 'hsl(var(--muted-foreground))' }
                        }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "hsl(var(--popover))",
                          border: "1px solid hsl(var(--border))",
                          borderRadius: "0.5rem",
                        }}
                      />
                      <Legend />
                      <Bar
                        dataKey="uptime_percent"
                        fill="#10B981"
                        name="Uptime %"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Last Updated */}
          <div className="text-center text-sm text-muted-foreground">
            Last updated: {new Date(statistics.timestamp * 1000).toLocaleString()}
          </div>
        </main>
      </div>
    </AppLayout>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  color: "blue" | "green" | "red" | "purple";
  iconColor: string;
}

function StatCard({ icon, title, value, iconColor }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={iconColor}>{icon}</div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
      </CardContent>
    </Card>
  );
}

interface ServiceCardProps {
  service: ServiceMetrics;
}

function ServiceCard({ service }: ServiceCardProps) {
  const isHealthy = service.status === "healthy";

  return (
    <Card className={`border-l-4 ${isHealthy ? 'border-l-green-500' : 'border-l-red-500'}`}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${isHealthy ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
              <Server className={`h-6 w-6 ${isHealthy ? 'text-green-600' : 'text-red-600'}`} />
            </div>
            <div>
              <CardTitle className="text-lg">{service.name}</CardTitle>
              <p className="text-sm text-muted-foreground">
                {service.address}:{service.port}
              </p>
            </div>
          </div>
          <Badge variant={isHealthy ? "default" : "destructive"}>
            {service.status.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Response Time</p>
            <p className="text-2xl font-bold">
              {service.current_response_time.toFixed(1)}
              <span className="text-sm font-normal text-muted-foreground">ms</span>
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Uptime</p>
            <p className="text-2xl font-bold">
              {service.uptime_percent.toFixed(2)}
              <span className="text-sm font-normal text-muted-foreground">%</span>
            </p>
          </div>
        </div>
        <div className="pt-4 border-t">
          <p className="text-xs text-muted-foreground">
            Last checked: {new Date(service.last_check * 1000).toLocaleString()}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
