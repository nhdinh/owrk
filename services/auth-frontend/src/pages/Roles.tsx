import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { roleAPI } from "@/lib/role-api";
import type { Role } from "@/types/auth";

// @ts-ignore - Module Federation remote import
import { AppLayout } from "shared_components/AppLayout";
// @ts-ignore - Module Federation remote import
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "shared_components/ui/table";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  // @ts-expect-error - Module Federation remote import
} from "shared_components/ui/card";

// @ts-expect-error - Module Federation remote import
import { Button } from "shared_components/ui/button";
// @ts-expect-error - Module Federation remote import
import { Badge } from "shared_components/ui/badge";
import { ArrowLeft, Shield, Plus, Eye, Trash2, Key } from "lucide-react";
import { toast } from "sonner";
// @ts-ignore - Module Federation remote import
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "shared_components/ui/dialog";
// @ts-expect-error - Module Federation remote import
import { Input } from "shared_components/ui/input";
// @ts-expect-error - Module Federation remote import
import { Label } from "shared_components/ui/label";
// @ts-expect-error - Module Federation remote import
import { Textarea } from "shared_components/ui/textarea";
import { useState } from "react";

export default function Roles() {
  const navigate = useNavigate();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    display_name: "",
    description: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    data: rolesData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["roles"],
    queryFn: () => roleAPI.list(),
  });

  const handleDelete = async (roleId: number) => {
    if (!confirm("Are you sure you want to delete this role?")) return;

    try {
      await roleAPI.delete(roleId);
      toast.success("Role deleted successfully");
      refetch();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to delete role");
    }
  };

  const handleCreateRole = async () => {
    if (!formData.name.trim() || !formData.display_name.trim()) {
      toast.error("Name and Display Name are required");
      return;
    }

    setIsSubmitting(true);
    try {
      await roleAPI.create(formData);
      toast.success("Role created successfully");
      setCreateDialogOpen(false);
      setFormData({ name: "", display_name: "", description: "" });
      refetch();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to create role");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppLayout>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => navigate("/")}
                >
                  <ArrowLeft className="h-5 w-5" />
                </Button>
                <div>
                  <h1 className="text-2xl font-bold flex items-center gap-2">
                    <Shield className="h-6 w-6" />
                    Role Management
                  </h1>
                  <p className="text-sm text-muted-foreground">
                    Configure roles and permissions
                  </p>
                </div>
              </div>
              <Button onClick={() => setCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Role
              </Button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          {/* Roles Table */}
          <Card>
            <CardHeader>
              <CardTitle>Roles ({rolesData?.total || 0})</CardTitle>
              <CardDescription>
                View and manage all system roles and permissions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-12">Loading roles...</div>
              ) : rolesData?.roles.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No roles found</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Role Name</TableHead>
                      <TableHead>Display Name</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Permissions</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {rolesData?.roles.map((role: Role) => (
                      <TableRow key={role.id}>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-primary/10 rounded flex items-center justify-center">
                              <Shield className="h-4 w-4 text-primary" />
                            </div>
                            <span className="font-medium">{role.name}</span>
                          </div>
                        </TableCell>
                        <TableCell>{role.display_name}</TableCell>
                        <TableCell className="max-w-xs truncate">
                          {role.description || "No description"}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="gap-1">
                            <Key className="h-3 w-3" />
                            {role.permissions?.length || 0} permissions
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={role.is_active ? "default" : "secondary"}
                          >
                            {role.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => navigate(`/roles/${role.id}`)}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDelete(role.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Role Information */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                About Roles & Permissions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">What are Roles?</h4>
                  <p className="text-sm text-muted-foreground">
                    Roles define a set of permissions that can be assigned to
                    users. Each user can have one role.
                  </p>
                </div>

                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">Permissions</h4>
                  <p className="text-sm text-muted-foreground">
                    Permissions control what actions users can perform in the
                    system. They are grouped by resource and action.
                  </p>
                </div>

                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">Best Practices</h4>
                  <p className="text-sm text-muted-foreground">
                    Create roles based on job functions and assign minimal
                    necessary permissions.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </main>

        {/* Create Role Dialog */}
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Create New Role</DialogTitle>
              <DialogDescription>
                Create a new role with permissions for your users
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Role Name</Label>
                <Input
                  id="name"
                  placeholder="e.g., manager, viewer, editor"
                  value={formData.name}
                  onChange={(e: any) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                />
                <p className="text-xs text-muted-foreground">
                  Lowercase identifier for the role (no spaces)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="display_name">Display Name</Label>
                <Input
                  id="display_name"
                  placeholder="e.g., Manager, Viewer, Editor"
                  value={formData.display_name}
                  onChange={(e: any) =>
                    setFormData({ ...formData, display_name: e.target.value })
                  }
                />
                <p className="text-xs text-muted-foreground">
                  Human-readable name shown in the UI
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Describe what this role is for..."
                  value={formData.description}
                  onChange={(e: any) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  rows={3}
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setCreateDialogOpen(false)}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button onClick={handleCreateRole} disabled={isSubmitting}>
                {isSubmitting ? "Creating..." : "Create Role"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
}
