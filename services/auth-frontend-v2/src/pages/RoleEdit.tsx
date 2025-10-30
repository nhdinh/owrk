import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { roleAPI } from '@/lib/role-api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { ArrowLeft, Save, X } from 'lucide-react';
import { toast } from 'sonner';
import { useState, useEffect } from 'react';

export default function RoleEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Fetch role data
  const { data: role, isLoading: roleLoading } = useQuery({
    queryKey: ['role', id],
    queryFn: () => roleAPI.get(parseInt(id!)),
    enabled: !!id,
  });

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    display_name: '',
    description: '',
    is_active: true,
  });

  // Initialize form with role data
  useEffect(() => {
    if (role) {
      setFormData({
        name: role.name || '',
        display_name: role.display_name || '',
        description: role.description || '',
        is_active: role.is_active,
      });
    }
  }, [role]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: typeof formData) => roleAPI.update(parseInt(id!), data),
    onSuccess: () => {
      toast.success('Role updated successfully');
      navigate(`/roles/${id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update role');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Basic validation
    if (!formData.name || !formData.display_name) {
      toast.error('Name and display name are required');
      return;
    }

    // Name validation (alphanumeric, lowercase, underscores only)
    const nameRegex = /^[a-z0-9_]+$/;
    if (!nameRegex.test(formData.name)) {
      toast.error('Name must contain only lowercase letters, numbers, and underscores');
      return;
    }

    updateMutation.mutate(formData);
  };

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  if (roleLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        Loading role data...
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

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate(`/roles/${id}`)}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold">Edit Role</h1>
                <p className="text-sm text-muted-foreground">{role.display_name}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Form */}
      <div className="container mx-auto px-4 py-8">
        <form onSubmit={handleSubmit}>
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Role Information</CardTitle>
              <CardDescription>
                Update role details. Fields marked with * are required.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Name */}
              <div className="space-y-2">
                <Label htmlFor="name">Name (System Key) *</Label>
                <Input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value.toLowerCase())}
                  placeholder="admin"
                  pattern="[a-z0-9_]+"
                  title="Only lowercase letters, numbers, and underscores allowed"
                  required
                />
                <p className="text-sm text-muted-foreground">
                  Used internally. Only lowercase letters, numbers, and underscores.
                </p>
              </div>

              {/* Display Name */}
              <div className="space-y-2">
                <Label htmlFor="display_name">Display Name *</Label>
                <Input
                  id="display_name"
                  type="text"
                  value={formData.display_name}
                  onChange={(e) => handleChange('display_name', e.target.value)}
                  placeholder="Administrator"
                  required
                />
                <p className="text-sm text-muted-foreground">
                  User-friendly name shown in the interface.
                </p>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  placeholder="Describe the role's purpose and permissions..."
                  rows={4}
                />
              </div>

              {/* Active Status */}
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) => handleChange('is_active', checked)}
                />
                <Label htmlFor="is_active" className="cursor-pointer">
                  Active Role
                </Label>
              </div>

              {/* Permissions Note */}
              <div className="bg-muted p-4 rounded-lg">
                <p className="text-sm text-muted-foreground">
                  <strong>Note:</strong> To manage permissions for this role, please use the role detail page
                  after saving. You can add or remove permissions there.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2 justify-end pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate(`/roles/${id}`)}
                  disabled={updateMutation.isPending}
                >
                  <X className="h-4 w-4 mr-2" />
                  Cancel
                </Button>
                <Button type="submit" disabled={updateMutation.isPending}>
                  <Save className="h-4 w-4 mr-2" />
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </form>
      </div>
    </div>
  );
}
