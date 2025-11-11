import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { userAPI } from "@/lib/user-api";
import { roleAPI } from "@/lib/role-api";
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
import { Input } from "shared_components/ui/input";
// @ts-expect-error - Module Federation remote import
import { Label } from "shared_components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowLeft, Save, X } from "lucide-react";
import { toast } from "sonner";
import { useState, useEffect } from "react";

// @ts-ignore - Module Federation remote import
import { AppLayout } from "shared_components/AppLayout";

export default function UserEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Fetch user data
  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ["user", id],
    queryFn: () => userAPI.get(parseInt(id!)),
    enabled: !!id,
  });

  // Fetch roles for dropdown
  const { data: rolesData } = useQuery({
    queryKey: ["roles"],
    queryFn: () => roleAPI.list(),
  });

  // Form state
  const [formData, setFormData] = useState({
    email: "",
    full_name: "",
    username: "",
    phone_number: "",
    position: "",
    address: "",
    role_id: undefined as number | undefined,
    is_active: true,
  });

  // Initialize form with user data
  useEffect(() => {
    if (user) {
      setFormData({
        email: user.email || "",
        full_name: user.full_name || "",
        username: user.username || "",
        phone_number: user.phone_number || "",
        position: user.position || "",
        address: user.address || "",
        role_id: user.role_id,
        is_active: user.is_active,
      });
    }
  }, [user]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: typeof formData) => userAPI.update(parseInt(id!), data),
    onSuccess: () => {
      toast.success("User updated successfully");
      navigate(`/users/${id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update user");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Basic validation
    if (!formData.email || !formData.full_name) {
      toast.error("Email and full name are required");
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      toast.error("Invalid email format");
      return;
    }

    updateMutation.mutate(formData);
  };

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  if (userLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        Loading user data...
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground mb-4">User not found</p>
            <Button onClick={() => navigate("/users")}>Back to Users</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

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
                  onClick={() => navigate(`/users/${id}`)}
                >
                  <ArrowLeft className="h-5 w-5" />
                </Button>
                <div>
                  <h1 className="text-2xl font-bold">Edit User</h1>
                  <p className="text-sm text-muted-foreground">{user.email}</p>
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
                <CardTitle>User Information</CardTitle>
                <CardDescription>
                  Update user details. Fields marked with * are required.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Email */}
                <div className="space-y-2">
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e: any) => handleChange("email", e.target.value)}
                    placeholder="user@example.com"
                    required
                  />
                </div>

                {/* Full Name */}
                <div className="space-y-2">
                  <Label htmlFor="full_name">Full Name *</Label>
                  <Input
                    id="full_name"
                    type="text"
                    value={formData.full_name}
                    onChange={(e: any) =>
                      handleChange("full_name", e.target.value)
                    }
                    placeholder="John Doe"
                    required
                  />
                </div>

                {/* Username */}
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    type="text"
                    value={formData.username}
                    onChange={(e: any) =>
                      handleChange("username", e.target.value)
                    }
                    placeholder="johndoe"
                  />
                </div>

                {/* Phone Number */}
                <div className="space-y-2">
                  <Label htmlFor="phone_number">Phone Number</Label>
                  <Input
                    id="phone_number"
                    type="tel"
                    value={formData.phone_number}
                    onChange={(e: any) =>
                      handleChange("phone_number", e.target.value)
                    }
                    placeholder="+1234567890"
                  />
                </div>

                {/* Position */}
                <div className="space-y-2">
                  <Label htmlFor="position">Position</Label>
                  <Input
                    id="position"
                    type="text"
                    value={formData.position}
                    onChange={(e: any) =>
                      handleChange("position", e.target.value)
                    }
                    placeholder="Software Engineer"
                  />
                </div>

                {/* Address */}
                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <Input
                    id="address"
                    type="text"
                    value={formData.address}
                    onChange={(e: any) =>
                      handleChange("address", e.target.value)
                    }
                    placeholder="123 Main St, City, Country"
                  />
                </div>

                {/* Role */}
                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <Select
                    value={formData.role_id?.toString() || "none"}
                    onValueChange={(value) =>
                      handleChange(
                        "role_id",
                        value === "none" ? undefined : parseInt(value)
                      )
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">No Role</SelectItem>
                      {rolesData?.roles.map((role) => (
                        <SelectItem key={role.id} value={role.id.toString()}>
                          {role.display_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Active Status */}
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="is_active"
                    checked={formData.is_active}
                    onCheckedChange={(checked) =>
                      handleChange("is_active", checked)
                    }
                  />
                  <Label htmlFor="is_active" className="cursor-pointer">
                    Active User
                  </Label>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 justify-end pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => navigate(`/users/${id}`)}
                    disabled={updateMutation.isPending}
                  >
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </Button>
                  <Button type="submit" disabled={updateMutation.isPending}>
                    <Save className="h-4 w-4 mr-2" />
                    {updateMutation.isPending ? "Saving..." : "Save Changes"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </form>
        </div>
      </div>
    </AppLayout>
  );
}
