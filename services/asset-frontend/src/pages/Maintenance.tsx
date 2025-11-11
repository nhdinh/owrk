import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { assetAPI } from "@/lib/asset-api";
import type { MaintenanceCreateRequest, Asset } from "@/types/asset";
// @ts-ignore - Module Federation remote import
import { AppLayout } from "shared_components/AppLayout";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Wrench,
  Plus,
  Filter,
  Calendar,
} from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";

interface MaintenanceRecord {
  id: number;
  asset_id: number;
  asset_code?: string;
  asset_name?: string;
  maintenance_type: string;
  maintenance_date: string;
  completed_date?: string | null;
  cost: string;
  technician?: string | null;
  description?: string | null;
  notes?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

interface MaintenanceFormData {
  asset_id: number;
  maintenance_type: string;
  maintenance_date: string;
  description: string;
  cost: string;
  technician: string;
  notes: string;
}

export default function Maintenance() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [formData, setFormData] = useState<MaintenanceFormData>({
    asset_id: 0,
    maintenance_type: "routine",
    maintenance_date: new Date().toISOString().split("T")[0],
    description: "",
    cost: "",
    technician: "",
    notes: "",
  });

  // Fetch maintenance records
  const {
    data: maintenanceRecords = [],
    isLoading: isLoadingMaintenance,
  } = useQuery<MaintenanceRecord[]>({
    queryKey: ["maintenance", statusFilter],
    queryFn: async (): Promise<MaintenanceRecord[]> => {
      const token = localStorage.getItem("access_token");
      const params = new URLSearchParams();
      if (statusFilter !== "all") {
        params.append("status", statusFilter);
      }

      const response = await fetch(
        `http://localhost:8000/api/v1/assets/maintenance/?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch maintenance records");
      }

      const data = await response.json();
      return data.maintenance_records || data || [];
    },
  });

  // Fetch assets for dropdown
  const { data: assetsData } = useQuery({
    queryKey: ["assets-simple"],
    queryFn: () => assetAPI.listAssets({}),
  });

  const assets = assetsData?.assets || [];

  const createMutation = useMutation({
    mutationFn: async (data: MaintenanceCreateRequest) => {
      const response = await fetch(`http://localhost:8000/api/v1/assets/maintenance/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create maintenance record");
      }

      return response.json();
    },
    onSuccess: () => {
      toast.success("Maintenance record created successfully");
      setCreateDialogOpen(false);
      setFormData({
        asset_id: 0,
        maintenance_type: "routine",
        maintenance_date: new Date().toISOString().split("T")[0],
        description: "",
        cost: "",
        technician: "",
        notes: "",
      });
      queryClient.invalidateQueries({ queryKey: ["maintenance"] });
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to create maintenance record");
    },
  });

  const handleCreateSubmit = () => {
    if (!formData.asset_id || !formData.maintenance_type || !formData.maintenance_date) {
      toast.error("Asset, type, and date are required");
      return;
    }

    createMutation.mutate({
      asset_id: formData.asset_id,
      maintenance_type: formData.maintenance_type,
      maintenance_date: formData.maintenance_date,
      description: formData.description || undefined,
      cost: formData.cost ? parseFloat(formData.cost) : undefined,
      technician: formData.technician || undefined,
      notes: formData.notes || undefined,
    });
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status?.toLowerCase()) {
      case "completed":
        return "default";
      case "in_progress":
        return "secondary";
      case "pending":
        return "outline";
      case "cancelled":
        return "destructive";
      default:
        return "outline";
    }
  };

  const getTypeBadgeVariant = (type: string) => {
    switch (type?.toLowerCase()) {
      case "emergency":
        return "destructive";
      case "corrective":
        return "secondary";
      case "preventive":
        return "default";
      default:
        return "outline";
    }
  };

  if (isLoadingMaintenance) {
    return (
      <AppLayout>
        <div className="min-h-screen flex items-center justify-center">
          Loading maintenance records...
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <Wrench className="h-6 w-6" />
                  Asset Maintenance
                </h1>
                <p className="text-sm text-muted-foreground">
                  Track and manage asset maintenance records
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Records</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
                <Button onClick={() => setCreateDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  New Maintenance
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          <Card>
            <CardHeader>
              <CardTitle>All Maintenance Records</CardTitle>
              <CardDescription>
                {maintenanceRecords.length} records found
              </CardDescription>
            </CardHeader>
            <CardContent>
              {maintenanceRecords.length === 0 ? (
                <div className="text-center py-12">
                  <Wrench className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No maintenance records yet</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Get started by creating your first maintenance record
                  </p>
                  <Button onClick={() => setCreateDialogOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Maintenance Record
                  </Button>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Asset</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Technician</TableHead>
                      <TableHead>Cost</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {maintenanceRecords.map((record) => (
                      <TableRow key={record.id}>
                        <TableCell className="font-medium">
                          {record.asset_code || `#${record.asset_id}`}
                          <br />
                          <span className="text-sm text-muted-foreground">
                            {record.asset_name}
                          </span>
                        </TableCell>
                        <TableCell>
                          <Badge variant={getTypeBadgeVariant(record.maintenance_type)}>
                            {record.maintenance_type}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3 text-muted-foreground" />
                            {format(new Date(record.maintenance_date), "MMM dd, yyyy")}
                          </div>
                        </TableCell>
                        <TableCell>{record.technician || "-"}</TableCell>
                        <TableCell>
                          {record.cost ? `$${parseFloat(record.cost).toFixed(2)}` : "-"}
                        </TableCell>
                        <TableCell>
                          <Badge variant={getStatusBadgeVariant(record.status)}>
                            {record.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="max-w-xs truncate">
                          {record.description || "-"}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm">
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </main>

        {/* Create Dialog */}
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>Create Maintenance Record</DialogTitle>
              <DialogDescription>
                Add a new maintenance record for an asset
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="asset_id">Asset *</Label>
                  <Select
                    value={formData.asset_id.toString()}
                    onValueChange={(value) =>
                      setFormData({ ...formData, asset_id: parseInt(value) })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select asset" />
                    </SelectTrigger>
                    <SelectContent>
                      {assets.map((asset: Asset) => (
                        <SelectItem key={asset.id} value={asset.id.toString()}>
                          {asset.code} - {asset.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maintenance_type">Type *</Label>
                  <Select
                    value={formData.maintenance_type}
                    onValueChange={(value) =>
                      setFormData({ ...formData, maintenance_type: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="routine">Routine</SelectItem>
                      <SelectItem value="preventive">Preventive</SelectItem>
                      <SelectItem value="corrective">Corrective</SelectItem>
                      <SelectItem value="emergency">Emergency</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="maintenance_date">Maintenance Date *</Label>
                  <Input
                    id="maintenance_date"
                    type="date"
                    value={formData.maintenance_date}
                    onChange={(e) =>
                      setFormData({ ...formData, maintenance_date: e.target.value })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cost">Cost</Label>
                  <Input
                    id="cost"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={formData.cost}
                    onChange={(e) =>
                      setFormData({ ...formData, cost: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="technician">Technician</Label>
                <Input
                  id="technician"
                  placeholder="Technician name"
                  value={formData.technician}
                  onChange={(e) =>
                    setFormData({ ...formData, technician: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe the maintenance work..."
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  rows={3}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  placeholder="Additional notes..."
                  value={formData.notes}
                  onChange={(e) =>
                    setFormData({ ...formData, notes: e.target.value })
                  }
                  rows={2}
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setCreateDialogOpen(false)}
                disabled={createMutation.isPending}
              >
                Cancel
              </Button>
              <Button onClick={handleCreateSubmit} disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create Record"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
}
