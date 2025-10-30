import { useAuth } from '@/lib/auth-context';
import { useQuery } from '@tanstack/react-query';
import { statsAPI } from '@/lib/stats-api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Users, Shield, LayoutDashboard, Settings, LogOut, UserCheck, ShieldCheck, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Fetch system statistics
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['systemStats'],
    queryFn: () => statsAPI.getSystemStats(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
              <LayoutDashboard className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Asset Management System</h1>
              <p className="text-sm text-muted-foreground">Authentication & User Management</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium">{user?.full_name}</p>
              <p className="text-xs text-muted-foreground">{user?.email}</p>
            </div>
            <Button variant="outline" size="icon" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold tracking-tight">
            Welcome back, {user?.full_name?.split(' ')[0]}!
          </h2>
          <p className="text-muted-foreground mt-2">
            Manage users, roles, and permissions for the asset management system
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
              )}
              <p className="text-xs text-muted-foreground">Active system users</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <UserCheck className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold text-green-600">{stats?.active_users || 0}</div>
              )}
              <p className="text-xs text-muted-foreground">
                {stats?.inactive_users || 0} inactive
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Roles</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold">{stats?.total_roles || 0}</div>
              )}
              <p className="text-xs text-muted-foreground">Defined roles</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">MFA Enabled</CardTitle>
              <ShieldCheck className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold text-blue-600">{stats?.users_with_mfa || 0}</div>
              )}
              <p className="text-xs text-muted-foreground">
                {stats?.total_users ?
                  `${Math.round((stats.users_with_mfa / stats.total_users) * 100)}% of users`
                  : 'No users'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Your Role Card */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Your Account
            </CardTitle>
            <CardDescription>Your current role and permissions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Role</p>
                <p className="text-lg font-semibold">{user?.role?.display_name || 'No Role'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Status</p>
                <div className="flex gap-2">
                  {user?.is_active && (
                    <span className="inline-flex items-center gap-1 text-sm font-medium text-green-600">
                      <UserCheck className="h-4 w-4" />
                      Active
                    </span>
                  )}
                  {user?.mfa_enabled && (
                    <span className="inline-flex items-center gap-1 text-sm font-medium text-blue-600">
                      <ShieldCheck className="h-4 w-4" />
                      MFA
                    </span>
                  )}
                </div>
              </div>
              <div className="flex items-end">
                <Button variant="outline" onClick={() => navigate('/profile')} className="w-full">
                  View Profile
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Navigation Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/users')}>
            <CardHeader>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-2">
                <Users className="w-6 h-6 text-primary" />
              </div>
              <CardTitle>User Management</CardTitle>
              <CardDescription>
                View, create, and manage user accounts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="ghost" className="w-full">
                Go to Users
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/roles')}>
            <CardHeader>
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-2">
                <Shield className="w-6 h-6 text-accent" />
              </div>
              <CardTitle>Role Management</CardTitle>
              <CardDescription>
                Configure roles and permissions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="ghost" className="w-full">
                Go to Roles
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/profile')}>
            <CardHeader>
              <div className="w-12 h-12 bg-secondary rounded-lg flex items-center justify-center mb-2">
                <Settings className="w-6 h-6 text-foreground" />
              </div>
              <CardTitle>Profile Settings</CardTitle>
              <CardDescription>
                Manage your account and security
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="ghost" className="w-full">
                Go to Profile
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* System Info */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              System Overview
            </CardTitle>
            <CardDescription>Quick system health and activity metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <h4 className="text-sm font-medium">User Statistics</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Total Users:</span>
                    <span className="font-medium">{stats?.total_users || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Active:</span>
                    <span className="font-medium text-green-600">{stats?.active_users || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Inactive:</span>
                    <span className="font-medium text-gray-600">{stats?.inactive_users || 0}</span>
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Security</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">MFA Enabled:</span>
                    <span className="font-medium text-blue-600">{stats?.users_with_mfa || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Recent Logins:</span>
                    <span className="font-medium">{stats?.recent_logins || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Total Roles:</span>
                    <span className="font-medium">{stats?.total_roles || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
