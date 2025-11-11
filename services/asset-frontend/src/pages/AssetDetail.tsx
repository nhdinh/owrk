import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";
import { assetAPI } from "@/lib/asset-api";
// @ts-ignore - Module Federation remote import
import { AppLayout } from "shared_components/AppLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Edit, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { AssetStatus, AssetType } from "@/types/asset";
// @ts-ignore - Module Federation remote import
import { useAuth } from "shared_components/AuthContext";

export default function AssetDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const { data: asset, isLoading } = useQuery({
    queryKey: ["asset", id],
    queryFn: () => assetAPI.get(Number(id)),
    enabled: !!id,
  });

  const deleteMutation = useMutation({
    mutationFn: assetAPI.delete,
    onSuccess: () => {
      toast.success("Asset deleted successfully");
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      navigate("/");
    },
    onError: () => {
      toast.error("Failed to delete asset");
    },
  });

  const handleDelete = () => {
    if (window.confirm("Are you sure you want to delete this asset?")) {
      deleteMutation.mutate(Number(id));
    }
  };

  const getStatusBadge = (status: AssetStatus) => {
    const variants: Record<AssetStatus, { variant: "default" | "secondary" | "destructive" | "outline"; label: string }> = {
      [AssetStatus.NEW]: { variant: "default", label: "New" },
      [AssetStatus.IN_USE]: { variant: "default", label: "In Use" },
      [AssetStatus.UNDER_MAINTENANCE]: { variant: "secondary", label: "Under Maintenance" },
      [AssetStatus.DAMAGED]: { variant: "destructive", label: "Damaged" },
      [AssetStatus.DISPOSED]: { variant: "outline", label: "Disposed" },
    };
    const config = variants[status];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getTypeBadge = (type: AssetType) => {
    return type === AssetType.FIXED_ASSET ? (
      <Badge variant="default">Fixed Asset</Badge>
    ) : (
      <Badge variant="secondary">Tool/Equipment</Badge>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("vi-VN");
  };

  if (isLoading) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading asset details...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (!asset) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="text-center">
            <p className="text-xl font-semibold">Asset not found</p>
            <Button onClick={() => navigate("/")} className="mt-4">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Assets
            </Button>
          </div>
        </div>
      </AppLayout>
    );
  }

  const canEdit = user?.id !== undefined;
  const canDelete = user?.id !== undefined;

  return (
    <AppLayout>
      <div className="min-h-screen bg-background">
        <div className="border-b">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">{asset.name}</h1>
                <p className="text-muted-foreground">Asset Code: {asset.code}</p>
              </div>
            <div className="flex items-center gap-2">
              {canEdit && (
                <Button onClick={() => navigate(`/assets/${id}/edit`)}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit
                </Button>
              )}
              {canDelete && (
                <Button
                  variant="destructive"
                  onClick={handleDelete}
                  disabled={deleteMutation.isPending}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <div className="grid gap-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Asset Type</p>
                  <div className="mt-1">{getTypeBadge(asset.asset_type)}</div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <div className="mt-1">{getStatusBadge(asset.status)}</div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Category</p>
                  <p className="font-medium">{asset.category?.name || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Manufacturer</p>
                  <p className="font-medium">{asset.manufacturer || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Model</p>
                  <p className="font-medium">{asset.model || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Serial Number</p>
                  <p className="font-medium">{asset.serial_number || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Year of Manufacture</p>
                  <p className="font-medium">{asset.year_of_manufacture || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Department</p>
                  <p className="font-medium">{asset.department?.name || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Location</p>
                  <p className="font-medium">{asset.location || "N/A"}</p>
                </div>
              </div>
              {asset.notes && (
                <div className="mt-4">
                  <p className="text-sm text-muted-foreground">Notes</p>
                  <p className="mt-1">{asset.notes}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Assignment Information */}
          {asset.assigned_to && (
            <Card>
              <CardHeader>
                <CardTitle>Current Assignment</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Assigned To</p>
                    <p className="font-medium">{asset.assigned_to.user_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Department</p>
                    <p className="font-medium">{asset.assigned_to.department_name}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Financial Information */}
          <Card>
            <CardHeader>
              <CardTitle>Financial Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Purchase Price</p>
                  <p className="font-medium">{formatCurrency(asset.purchase_price)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Purchase Date</p>
                  <p className="font-medium">{formatDate(asset.purchase_date)}</p>
                </div>
                {asset.current_value !== undefined && (
                  <div>
                    <p className="text-sm text-muted-foreground">Current Value</p>
                    <p className="font-medium">{formatCurrency(asset.current_value)}</p>
                  </div>
                )}
                {asset.depreciation_method && (
                  <>
                    <div>
                      <p className="text-sm text-muted-foreground">Depreciation Method</p>
                      <p className="font-medium">{asset.depreciation_method}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Depreciation Years</p>
                      <p className="font-medium">{asset.depreciation_years || "N/A"}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Salvage Value</p>
                      <p className="font-medium">
                        {asset.salvage_value ? formatCurrency(asset.salvage_value) : "N/A"}
                      </p>
                    </div>
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Warranty Information */}
          {asset.warranty_start_date && (
            <Card>
              <CardHeader>
                <CardTitle>Warranty Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Warranty Start</p>
                    <p className="font-medium">{formatDate(asset.warranty_start_date)}</p>
                  </div>
                  {asset.warranty_end_date && (
                    <div>
                      <p className="text-sm text-muted-foreground">Warranty End</p>
                      <p className="font-medium">{formatDate(asset.warranty_end_date)}</p>
                    </div>
                  )}
                  <div>
                    <p className="text-sm text-muted-foreground">Warranty Period</p>
                    <p className="font-medium">{asset.warranty_months} months</p>
                  </div>
                  {asset.warranty_provider && (
                    <div>
                      <p className="text-sm text-muted-foreground">Warranty Provider</p>
                      <p className="font-medium">{asset.warranty_provider}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* History Tabs */}
          <Card>
            <CardHeader>
              <CardTitle>History</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="assignment">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="assignment">Assignment History</TabsTrigger>
                  <TabsTrigger value="maintenance">Maintenance History</TabsTrigger>
                </TabsList>
                <TabsContent value="assignment" className="space-y-4">
                  {asset.assignment_history && asset.assignment_history.length > 0 ? (
                    <div className="space-y-4">
                      {asset.assignment_history.map((history) => (
                        <div key={history.id} className="border rounded-lg p-4">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm text-muted-foreground">Assigned To</p>
                              <p className="font-medium">{history.assigned_to_user}</p>
                            </div>
                            <div>
                              <p className="text-sm text-muted-foreground">Status</p>
                              <Badge>{history.status}</Badge>
                            </div>
                            <div>
                              <p className="text-sm text-muted-foreground">Assigned Date</p>
                              <p>{formatDate(history.assigned_date)}</p>
                            </div>
                            {history.reclaimed_date && (
                              <div>
                                <p className="text-sm text-muted-foreground">Reclaimed Date</p>
                                <p>{formatDate(history.reclaimed_date)}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-center text-muted-foreground py-8">No assignment history</p>
                  )}
                </TabsContent>
                <TabsContent value="maintenance" className="space-y-4">
                  {asset.maintenance_history && asset.maintenance_history.length > 0 ? (
                    <div className="space-y-4">
                      {asset.maintenance_history.map((history) => (
                        <div key={history.id} className="border rounded-lg p-4">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm text-muted-foreground">Type</p>
                              <p className="font-medium">{history.type}</p>
                            </div>
                            <div>
                              <p className="text-sm text-muted-foreground">Date</p>
                              <p>{formatDate(history.date)}</p>
                            </div>
                            <div>
                              <p className="text-sm text-muted-foreground">Cost</p>
                              <p className="font-medium">{formatCurrency(history.cost)}</p>
                            </div>
                          </div>
                          {history.notes && (
                            <div className="mt-4">
                              <p className="text-sm text-muted-foreground">Notes</p>
                              <p>{history.notes}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-center text-muted-foreground py-8">No maintenance history</p>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
      </div>
    </AppLayout>
  );
}
