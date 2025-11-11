import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { assetAPI } from "@/lib/asset-api";
import type { Asset, AssetStatus, AssetType } from "@/types/asset";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Package,
  Plus,
  Search,
  Eye,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Pencil,
} from "lucide-react";
import { toast } from "sonner";

export default function Assets() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);

  const {
    data: assetsData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: [
      "assets",
      search,
      categoryFilter,
      statusFilter,
      typeFilter,
      page,
      pageSize,
    ],
    queryFn: () =>
      assetAPI.list({
        page,
        page_size: pageSize,
        search: search || undefined,
        category_id: categoryFilter ? parseInt(categoryFilter) : undefined,
        status: statusFilter as AssetStatus | undefined,
        asset_type: typeFilter as AssetType | undefined,
      }),
  });

  const { data: categoriesData } = useQuery({
    queryKey: ["categories"],
    queryFn: () => assetAPI.getCategories(),
  });

  const handleDelete = async (assetId: number) => {
    if (!confirm("Are you sure you want to delete this asset?")) return;

    try {
      await assetAPI.delete(assetId);
      toast.success("Asset deleted successfully");
      refetch();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to delete asset");
    }
  };

  const getStatusBadgeVariant = (
    status: AssetStatus
  ): "default" | "secondary" | "destructive" | "outline" => {
    switch (status) {
      case "new":
        return "default";
      case "in_use":
        return "default";
      case "under_maintenance":
        return "secondary";
      case "damaged":
        return "destructive";
      case "disposed":
        return "outline";
      default:
        return "outline";
    }
  };

  const getStatusLabel = (status: AssetStatus): string => {
    switch (status) {
      case "new":
        return "New";
      case "in_use":
        return "In Use";
      case "under_maintenance":
        return "Under Maintenance";
      case "damaged":
        return "Damaged";
      case "disposed":
        return "Disposed";
      default:
        return status;
    }
  };

  const totalPages = assetsData ? Math.ceil(assetsData.total / pageSize) : 1;

  return (
    <AppLayout>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <Package className="h-6 w-6" />
                  Asset Management
                </h1>
                <p className="text-sm text-muted-foreground">
                  Manage company assets and equipment
                </p>
              </div>
              <Button onClick={() => navigate("/assets/new")}>
                <Plus className="h-4 w-4 mr-2" />
                Add Asset
              </Button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          {/* Filters */}
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="grid gap-4 md:grid-cols-5">
                <div className="md:col-span-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search by code, name, or serial number..."
                      value={search}
                      onChange={(e) => {
                        setSearch(e.target.value);
                        setPage(1);
                      }}
                      className="pl-10"
                    />
                  </div>
                </div>
                <Select
                  value={categoryFilter || "all"}
                  onValueChange={(value) => {
                    setCategoryFilter(value === "all" ? "" : value);
                    setPage(1);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categoriesData?.map((category) => (
                      <SelectItem
                        key={category.id}
                        value={category.id.toString()}
                      >
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select
                  value={typeFilter || "all"}
                  onValueChange={(value) => {
                    setTypeFilter(value === "all" ? "" : value);
                    setPage(1);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All Types" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="fixed_asset">Fixed Asset</SelectItem>
                    <SelectItem value="tool_equipment">
                      Tool/Equipment
                    </SelectItem>
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
                    <SelectItem value="new">New</SelectItem>
                    <SelectItem value="in_use">In Use</SelectItem>
                    <SelectItem value="under_maintenance">
                      Under Maintenance
                    </SelectItem>
                    <SelectItem value="damaged">Damaged</SelectItem>
                    <SelectItem value="disposed">Disposed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Assets Table */}
          <Card>
            <CardHeader>
              <CardTitle>Assets ({assetsData?.total || 0})</CardTitle>
              <CardDescription>
                Showing {assetsData?.assets.length || 0} of{" "}
                {assetsData?.total || 0} assets
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-12">Loading assets...</div>
              ) : assetsData?.assets.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Package className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No assets found</p>
                </div>
              ) : (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Code</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Category</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Assigned To</TableHead>
                        <TableHead>Purchase Price</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {assetsData?.assets.map((asset: Asset) => (
                        <TableRow key={asset.id}>
                          <TableCell className="font-medium">
                            {asset.code}
                          </TableCell>
                          <TableCell>
                            <div>
                              <div className="font-medium">{asset.name}</div>
                              {asset.model && (
                                <div className="text-sm text-muted-foreground">
                                  {asset.manufacturer} {asset.model}
                                </div>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            {asset.category ? (
                              <Badge variant="outline">
                                {asset.category.name}
                              </Badge>
                            ) : (
                              <span className="text-muted-foreground">N/A</span>
                            )}
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary">
                              {asset.asset_type === "fixed_asset"
                                ? "Fixed Asset"
                                : "Tool/Equipment"}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={getStatusBadgeVariant(asset.status)}
                            >
                              {getStatusLabel(asset.status)}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {asset.assigned_to ? (
                              <div className="text-sm">
                                <div>{asset.assigned_to.user_name}</div>
                                <div className="text-muted-foreground">
                                  {asset.assigned_to.department_name}
                                </div>
                              </div>
                            ) : (
                              <span className="text-muted-foreground">
                                Unassigned
                              </span>
                            )}
                          </TableCell>
                          <TableCell>
                            {new Intl.NumberFormat("vi-VN", {
                              style: "currency",
                              currency: "VND",
                            }).format(asset.purchase_price)}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end items-center space-x-2">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => navigate(`/assets/${asset.id}`)}
                                title="View Details"
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() =>
                                  navigate(`/assets/${asset.id}/edit`)
                                }
                                title="Edit Asset"
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleDelete(asset.id)}
                                title="Delete Asset"
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
      </div>
    </AppLayout>
  );
}
