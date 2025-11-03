import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { userAPI } from "@/lib/user-api";
import { roleAPI } from "@/lib/role-api";
import type { User } from "@/types/auth";
import { AppLayout } from "@/components/AppLayout";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Label } from "@/components/ui/label";
import {
  
  Users as UsersIcon,
  UserPlus,
  Search,
  Shield,
  Eye,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Pencil,
} from "lucide-react";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

const createUserSchema = z.object({
  email: z.string().email("Invalid email address"),
  full_name: z.string().min(1, "Full name is required"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  username: z.string().optional(),
  role_id: z.string().optional(),
  phone_number: z.string().optional(),
  position: z.string().optional(),
});

type CreateUserFormData = z.infer<typeof createUserSchema>;

export default function Users() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CreateUserFormData>({
    resolver: zodResolver(createUserSchema),
  });

  const {
    data: usersData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["users", search, roleFilter, statusFilter, page, pageSize],
    queryFn: () =>
      userAPI.list({
        skip: (page - 1) * pageSize,
        limit: pageSize,
        search: search || undefined,
        role_id: roleFilter ? parseInt(roleFilter) : undefined,
        is_active: statusFilter ? statusFilter === "active" : undefined,
      }),
  });

  const { data: rolesData } = useQuery({
    queryKey: ["roles"],
    queryFn: () => roleAPI.list(),
  });

  const handleDelete = async (userId: number) => {
    if (!confirm("Are you sure you want to delete this user?")) return;

    try {
      await userAPI.delete(userId);
      toast.success("User deleted successfully");
      refetch();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to delete user");
    }
  };

  const onCreateUser = async (data: CreateUserFormData) => {
    setIsCreating(true);

    try {
      await userAPI.create({
        email: data.email,
        full_name: data.full_name,
        password: data.password,
        username: data.username,
        role_id: data.role_id ? parseInt(data.role_id) : undefined,
        phone_number: data.phone_number,
        position: data.position,
      });
      toast.success("User created successfully");
      setCreateDialogOpen(false);
      reset();
      refetch();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to create user");
    } finally {
      setIsCreating(false);
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const totalPages = usersData ? Math.ceil(usersData.total / pageSize) : 1;

  return (
    <AppLayout>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="container mx-auto px-4 py-4 lg:px-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <UsersIcon className="h-6 w-6" />
                  User Management
                </h1>
                <p className="text-sm text-muted-foreground">
                  Manage system users and their permissions
                </p>
              </div>
              <Button onClick={() => setCreateDialogOpen(true)}>
                <UserPlus className="h-4 w-4 mr-2" />
                Add User
              </Button>
            </div>
          </div>
        </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="grid gap-4 md:grid-cols-4">
              <div className="md:col-span-2">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by name, email, or username..."
                    value={search}
                    onChange={(e) => {
                      setSearch(e.target.value);
                      setPage(1); // Reset to first page on search
                    }}
                    className="pl-10"
                  />
                </div>
              </div>
              <Select
                value={roleFilter || "all"}
                onValueChange={(value) => {
                  setRoleFilter(value === "all" ? "" : value);
                  setPage(1);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All Roles" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Roles</SelectItem>
                  {rolesData?.roles.map((role) => (
                    <SelectItem key={role.id} value={role.id.toString()}>
                      {role.display_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select
                value={statusFilter || "all"}
                onValueChange={(value) => {
                  setStatusFilter(value === "all" ? "" : value);
                  setPage(1);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Users Table */}
        <Card>
          <CardHeader>
            <CardTitle>Users ({usersData?.total || 0})</CardTitle>
            <CardDescription>
              Showing {usersData?.users.length || 0} of {usersData?.total || 0}{" "}
              users
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-12">Loading users...</div>
            ) : usersData?.users.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <UsersIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No users found</p>
              </div>
            ) : (
              <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>MFA</TableHead>
                      <TableHead>Last Login</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {usersData?.users.map((user: User) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <Avatar>
                              <AvatarFallback className="bg-primary/10 text-primary">
                                {getInitials(user.full_name)}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <div className="font-medium">
                                {user.full_name}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {user.username || "No username"}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>
                          {user.role ? (
                            <Badge variant="outline" className="gap-1">
                              <Shield className="h-3 w-3" />
                              {user.role.display_name}
                            </Badge>
                          ) : (
                            <span className="text-muted-foreground">
                              No role
                            </span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={user.is_active ? "default" : "secondary"}
                          >
                            {user.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={user.mfa_enabled ? "default" : "outline"}
                          >
                            {user.mfa_enabled ? "Enabled" : "Disabled"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {user.last_login_at
                            ? new Date(user.last_login_at).toLocaleDateString()
                            : "Never"}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end items-center space-x-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => navigate(`/users/${user.id}`)}
                              title="View Details"
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => navigate(`/users/${user.id}/edit`)}
                              title="Edit User"
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDelete(user.id)}
                              title="Delete User"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination */}
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-muted-foreground">
                    Page {page} of {totalPages}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        setPage((p) => Math.min(totalPages, p + 1))
                      }
                      disabled={page === totalPages}
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </main>

      {/* Create User Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create New User</DialogTitle>
            <DialogDescription>
              Add a new user to the system. They will receive an email with
              login instructions.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit(onCreateUser)}>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="email">Email *</Label>
                <Input id="email" type="email" {...register("email")} />
                {errors.email && (
                  <p className="text-sm text-destructive">
                    {errors.email.message}
                  </p>
                )}
              </div>

              <div className="grid gap-2">
                <Label htmlFor="full_name">Full Name *</Label>
                <Input id="full_name" {...register("full_name")} />
                {errors.full_name && (
                  <p className="text-sm text-destructive">
                    {errors.full_name.message}
                  </p>
                )}
              </div>

              <div className="grid gap-2">
                <Label htmlFor="password">Password *</Label>
                <Input
                  id="password"
                  type="password"
                  {...register("password")}
                />
                {errors.password && (
                  <p className="text-sm text-destructive">
                    {errors.password.message}
                  </p>
                )}
              </div>

              <div className="grid gap-2">
                <Label htmlFor="username">Username</Label>
                <Input id="username" {...register("username")} />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="role_id">Role</Label>
                <Select
                  onValueChange={(value) =>
                    register("role_id").onChange({ target: { value } })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role" />
                  </SelectTrigger>
                  <SelectContent>
                    {rolesData?.roles.map((role) => (
                      <SelectItem key={role.id} value={role.id.toString()}>
                        {role.display_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="phone_number">Phone Number</Label>
                <Input id="phone_number" {...register("phone_number")} />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="position">Position</Label>
                <Input id="position" {...register("position")} />
              </div>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setCreateDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isCreating}>
                {isCreating ? "Creating..." : "Create User"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
    </AppLayout>
  );
}
