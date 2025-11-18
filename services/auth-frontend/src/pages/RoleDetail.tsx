import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { roleAPI } from '@/lib/role-api';
// @ts-expect-error - Module Federation remote import
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from 'shared_components/ui/card';
// @ts-expect-error - Module Federation remote import
import { Button } from 'shared_components/ui/button';
// @ts-expect-error - Module Federation remote import
import { Badge } from 'shared_components/ui/badge';
// @ts-expect-error - Module Federation remote import
import { Separator } from 'shared_components/ui/separator';
// @ts-expect-error - Module Federation remote import
import { Tabs, TabsContent, TabsList, TabsTrigger } from 'shared_components/ui/tabs';
import { ArrowLeft, Shield, Edit, Trash2, Key, Plus, X } from 'lucide-react';
import { toast } from 'sonner';
import { format } from 'date-fns';

export default function RoleDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: role, isLoading, refetch } = useQuery({
    queryKey: ['role', id],
    queryFn: () => roleAPI.get(id!),
    enabled: !!id,
  });

  const { data: allPermissions } = useQuery({
    queryKey: ['permissions'],
    queryFn: () => roleAPI.getPermissions(),
  });

  const handleDelete = async () => {
    if (!role || !confirm('Are you sure you want to delete this role?')) return;

    try {
      await roleAPI.delete(role.id);
      toast.success('Role deleted successfully');
      navigate('/roles');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete role');
    }
  };

  const handleRemovePermission = async (permissionId: number) => {
    if (!role) return;

    try {
      await roleAPI.removePermission(role.id, permissionId);
      toast.success('Permission removed');
      refetch();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to remove permission');
    }
  };

  const handleAddPermission = async (permissionId: number) => {
    if (!role) return;

    try {
      await roleAPI.addPermission(role.id, permissionId);
      toast.success('Permission added');
      refetch();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to add permission');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        Loading role details...
      </div>
    );
  }

  if (!role) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground mb-4">Role not found</p>
            <Button onClick={() => navigate('/roles')}>Back to Roles</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const unassignedPermissions = allPermissions?.filter(
    (p) => !role.permissions?.some((rp) => rp.id === p.id)
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate('/roles')}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <Shield className="h-6 w-6" />
                  {role.display_name}
                </h1>
                <p className="text-sm text-muted-foreground">{role.name}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => navigate(`/roles/${role.id}/edit`)}>
                <Edit className="h-4 w-4 mr-2" />
                Edit
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
          {/* Info Card */}
          <Card className="md:col-span-1">
            <CardHeader>
              <div className="w-16 h-16 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <Shield className="h-8 w-8 text-primary" />
              </div>
              <CardTitle>{role.display_name}</CardTitle>
              <CardDescription>{role.name}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Badge variant={role.is_active ? 'default' : 'secondary'}>
                  {role.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>

              <Separator />

              <div className="space-y-2 text-sm">
                <div>
                  <label className="text-muted-foreground">Role ID</label>
                  <p className="font-medium">#{role.id}</p>
                </div>

                <div>
                  <label className="text-muted-foreground">Description</label>
                  <p className="text-sm">{role.description || 'No description'}</p>
                </div>

                <div>
                  <label className="text-muted-foreground">Permissions</label>
                  <p className="font-medium">{role.permissions?.length || 0} assigned</p>
                </div>

                <div>
                  <label className="text-muted-foreground">Created</label>
                  <p className="text-sm">{format(new Date(role.created_at), 'PPP')}</p>
                </div>

                <div>
                  <label className="text-muted-foreground">Updated</label>
                  <p className="text-sm">{format(new Date(role.updated_at), 'PPP')}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Permissions Tabs */}
          <Card className="md:col-span-2">
            <Tabs defaultValue="assigned">
              <CardHeader>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="assigned">
                    Assigned Permissions ({role.permissions?.length || 0})
                  </TabsTrigger>
                  <TabsTrigger value="available">
                    Available ({unassignedPermissions?.length || 0})
                  </TabsTrigger>
                </TabsList>
              </CardHeader>

              <CardContent>
                <TabsContent value="assigned" className="space-y-4">
                  {role.permissions && role.permissions.length > 0 ? (
                    <div className="grid gap-3">
                      {role.permissions.map((permission) => (
                        <div
                          key={permission.id}
                          className="flex items-start justify-between p-3 border rounded-lg hover:bg-accent/50 transition-colors"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Key className="h-4 w-4 text-primary" />
                              <h4 className="font-medium">{permission.name}</h4>
                            </div>
                            <p className="text-sm text-muted-foreground">
                              {permission.description || 'No description'}
                            </p>
                            <div className="flex gap-2 mt-2">
                              {permission.resource && (
                                <Badge variant="outline" className="text-xs">
                                  {permission.resource}
                                </Badge>
                              )}
                              {permission.action && (
                                <Badge variant="outline" className="text-xs">
                                  {permission.action}
                                </Badge>
                              )}
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleRemovePermission(permission.id)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      <Key className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No permissions assigned to this role</p>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="available" className="space-y-4">
                  {unassignedPermissions && unassignedPermissions.length > 0 ? (
                    <div className="grid gap-3">
                      {unassignedPermissions.map((permission) => (
                        <div
                          key={permission.id}
                          className="flex items-start justify-between p-3 border rounded-lg hover:bg-accent/50 transition-colors"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Key className="h-4 w-4 text-muted-foreground" />
                              <h4 className="font-medium">{permission.name}</h4>
                            </div>
                            <p className="text-sm text-muted-foreground">
                              {permission.description || 'No description'}
                            </p>
                            <div className="flex gap-2 mt-2">
                              {permission.resource && (
                                <Badge variant="outline" className="text-xs">
                                  {permission.resource}
                                </Badge>
                              )}
                              {permission.action && (
                                <Badge variant="outline" className="text-xs">
                                  {permission.action}
                                </Badge>
                              )}
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleAddPermission(permission.id)}
                          >
                            <Plus className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      <Key className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>All permissions are assigned to this role</p>
                    </div>
                  )}
                </TabsContent>
              </CardContent>
            </Tabs>
          </Card>
        </div>
      </main>
    </div>
  );
}
