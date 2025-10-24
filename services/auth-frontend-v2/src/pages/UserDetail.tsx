import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { userAPI } from '@/lib/user-api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  ArrowLeft,
  Mail,
  Phone,
  MapPin,
  Shield,
  Clock,
  Calendar,
  Edit,
  Trash2,
  Lock,
  Unlock,
} from 'lucide-react';
import { toast } from 'sonner';
import { format } from 'date-fns';

export default function UserDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: user, isLoading, refetch } = useQuery({
    queryKey: ['user', id],
    queryFn: () => userAPI.get(parseInt(id!)),
    enabled: !!id,
  });

  const handleToggleStatus = async () => {
    if (!user) return;

    try {
      if (user.is_active) {
        await userAPI.deactivate(user.id);
        toast.success('User deactivated');
      } else {
        await userAPI.activate(user.id);
        toast.success('User activated');
      }
      refetch();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update user status');
    }
  };

  const handleDelete = async () => {
    if (!user || !confirm('Are you sure you want to delete this user?')) return;

    try {
      await userAPI.delete(user.id);
      toast.success('User deleted successfully');
      navigate('/users');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete user');
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        Loading user details...
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground mb-4">User not found</p>
            <Button onClick={() => navigate('/users')}>Back to Users</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate('/users')}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold">User Details</h1>
                <p className="text-sm text-muted-foreground">{user.email}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => navigate(`/users/${user.id}/edit`)}>
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button variant="outline" onClick={handleToggleStatus}>
                {user.is_active ? (
                  <>
                    <Lock className="h-4 w-4 mr-2" />
                    Deactivate
                  </>
                ) : (
                  <>
                    <Unlock className="h-4 w-4 mr-2" />
                    Activate
                  </>
                )}
              </Button>
              <Button variant="destructive" onClick={handleDelete}>
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid gap-6 md:grid-cols-3">
          {/* Profile Card */}
          <Card className="md:col-span-1">
            <CardHeader className="text-center pb-4">
              <Avatar className="w-24 h-24 mx-auto mb-4">
                <AvatarFallback className="bg-primary text-primary-foreground text-2xl">
                  {getInitials(user.full_name)}
                </AvatarFallback>
              </Avatar>
              <CardTitle className="text-xl">{user.full_name}</CardTitle>
              <CardDescription>{user.position || 'No position'}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-center gap-2">
                <Badge variant={user.is_active ? 'default' : 'secondary'}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </Badge>
                {user.is_superuser && <Badge variant="destructive">Admin</Badge>}
              </div>

              <Separator />

              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <span className="truncate">{user.email}</span>
                </div>

                {user.phone_number && (
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <span>{user.phone_number}</span>
                  </div>
                )}

                {user.address && (
                  <div className="flex items-start gap-2 text-sm">
                    <MapPin className="h-4 w-4 text-muted-foreground mt-0.5" />
                    <span className="text-muted-foreground">{user.address}</span>
                  </div>
                )}

                {user.role && (
                  <div className="flex items-center gap-2 text-sm">
                    <Shield className="h-4 w-4 text-muted-foreground" />
                    <span>{user.role.display_name}</span>
                  </div>
                )}
              </div>

              <Separator />

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">MFA Enabled:</span>
                  <Badge variant={user.mfa_enabled ? 'default' : 'outline'}>
                    {user.mfa_enabled ? 'Yes' : 'No'}
                  </Badge>
                </div>

                <div className="flex justify-between">
                  <span className="text-muted-foreground">Email Verified:</span>
                  <Badge variant={user.email_verified ? 'default' : 'outline'}>
                    {user.email_verified ? 'Yes' : 'No'}
                  </Badge>
                </div>

                <div className="flex justify-between">
                  <span className="text-muted-foreground">User Type:</span>
                  <span className="capitalize">{user.user_type || 'local'}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Details Tabs */}
          <Card className="md:col-span-2">
            <Tabs defaultValue="info">
              <CardHeader>
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="info">Information</TabsTrigger>
                  <TabsTrigger value="security">Security</TabsTrigger>
                  <TabsTrigger value="activity">Activity</TabsTrigger>
                </TabsList>
              </CardHeader>

              <CardContent>
                <TabsContent value="info" className="space-y-4">
                  <div className="grid gap-4">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">User ID</label>
                      <p className="mt-1">#{user.id}</p>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Username</label>
                      <p className="mt-1">{user.username || 'Not set'}</p>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Department</label>
                      <p className="mt-1">
                        {user.department_id ? `Department #${user.department_id}` : 'Not assigned'}
                      </p>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Created At</label>
                      <div className="flex items-center gap-2 mt-1">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span>{format(new Date(user.created_at), 'PPP')}</span>
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Updated At</label>
                      <div className="flex items-center gap-2 mt-1">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span>{format(new Date(user.updated_at), 'PPP')}</span>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="security" className="space-y-4">
                  <div className="grid gap-4">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">
                        Last Login
                      </label>
                      <div className="flex items-center gap-2 mt-1">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span>{user.last_login_at || 'Never'}</span>
                      </div>
                      {user.last_login_ip && (
                        <p className="text-sm text-muted-foreground mt-1">
                          From IP: {user.last_login_ip}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="text-sm font-medium text-muted-foreground">
                        Password Changed
                      </label>
                      <p className="mt-1">{user.password_changed_at || 'Never'}</p>
                    </div>

                    <Separator />

                    <div className="space-y-2">
                      <Button variant="outline" className="w-full">
                        Reset Password
                      </Button>
                      <Button variant="outline" className="w-full">
                        {user.mfa_enabled ? 'Disable MFA' : 'Enable MFA'}
                      </Button>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="activity" className="space-y-4">
                  <div className="text-center py-12 text-muted-foreground">
                    <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No activity history available</p>
                  </div>
                </TabsContent>
              </CardContent>
            </Tabs>
          </Card>
        </div>
      </main>
    </div>
  );
}
