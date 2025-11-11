import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { assetAPI } from "@/lib/asset-api";
// @ts-ignore - Module Federation remote import
import { AppLayout } from "shared_components/AppLayout";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Save } from "lucide-react";
import { toast } from "sonner";
import {
  AssetStatus,
  AssetType,
  AssetCreateRequest,
  AssetUpdateRequest,
} from "@/types/asset";

const assetFormSchema = z.object({
  code: z.string().min(1, "Asset code is required"),
  name: z.string().min(1, "Asset name is required"),
  asset_type: z.nativeEnum(AssetType),
  category_id: z.number().min(1, "Category is required"),
  manufacturer: z.string().optional(),
  model: z.string().optional(),
  serial_number: z.string().optional(),
  year_of_manufacture: z
    .number()
    .min(1900)
    .max(new Date().getFullYear())
    .optional(),
  purchase_price: z.number().min(0, "Purchase price must be positive"),
  purchase_date: z.string().min(1, "Purchase date is required"),
  depreciation_method: z.string().optional(),
  depreciation_years: z.number().min(1).optional(),
  salvage_value: z.number().min(0).optional(),
  warranty_start_date: z.string().optional(),
  warranty_months: z.number().min(0).optional(),
  warranty_provider: z.string().optional(),
  department_id: z.number().optional(),
  location: z.string().optional(),
  status: z.nativeEnum(AssetStatus),
  notes: z.string().optional(),
});

type AssetFormValues = z.infer<typeof assetFormSchema>;

export default function AssetForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditMode = !!id;

  const { data: asset, isLoading: assetLoading } = useQuery({
    queryKey: ["asset", id],
    queryFn: () => assetAPI.get(Number(id)),
    enabled: isEditMode,
  });

  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: assetAPI.getCategories,
  });

  const form = useForm<AssetFormValues>({
    resolver: zodResolver(assetFormSchema),
    defaultValues: {
      code: "",
      name: "",
      asset_type: AssetType.FIXED_ASSET,
      category_id: 0,
      manufacturer: "",
      model: "",
      serial_number: "",
      purchase_price: 0,
      purchase_date: new Date().toISOString().split("T")[0],
      status: AssetStatus.NEW,
      notes: "",
    },
  });

  // Update form when asset data loads
  React.useEffect(() => {
    if (asset) {
      form.reset({
        code: asset.code,
        name: asset.name,
        asset_type: asset.asset_type,
        category_id: asset.category_id || 0,
        manufacturer: asset.manufacturer || "",
        model: asset.model || "",
        serial_number: asset.serial_number || "",
        year_of_manufacture: asset.year_of_manufacture,
        purchase_price: asset.purchase_price,
        purchase_date: asset.purchase_date,
        depreciation_method: asset.depreciation_method || "",
        depreciation_years: asset.depreciation_years,
        salvage_value: asset.salvage_value,
        warranty_start_date: asset.warranty_start_date || "",
        warranty_months: asset.warranty_months,
        warranty_provider: asset.warranty_provider || "",
        department_id: asset.department_id,
        location: asset.location || "",
        status: asset.status,
        notes: asset.notes || "",
      });
    }
  }, [asset, form]);

  const createMutation = useMutation({
    mutationFn: assetAPI.create,
    onSuccess: () => {
      toast.success("Asset created successfully");
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      navigate("/");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to create asset");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: AssetUpdateRequest }) =>
      assetAPI.update(id, data),
    onSuccess: () => {
      toast.success("Asset updated successfully");
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      queryClient.invalidateQueries({ queryKey: ["asset", id] });
      navigate(`/assets/${id}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update asset");
    },
  });

  const onSubmit = (data: AssetFormValues) => {
    if (isEditMode) {
      const updateData: AssetUpdateRequest = {
        name: data.name,
        category_id: data.category_id,
        manufacturer: data.manufacturer,
        model: data.model,
        serial_number: data.serial_number,
        year_of_manufacture: data.year_of_manufacture,
        purchase_price: data.purchase_price,
        purchase_date: data.purchase_date,
        depreciation_method: data.depreciation_method,
        depreciation_years: data.depreciation_years,
        salvage_value: data.salvage_value,
        warranty_start_date: data.warranty_start_date,
        warranty_months: data.warranty_months,
        warranty_provider: data.warranty_provider,
        department_id: data.department_id,
        location: data.location,
        status: data.status,
        notes: data.notes,
      };
      updateMutation.mutate({ id: Number(id), data: updateData });
    } else {
      const createData: AssetCreateRequest = {
        code: data.code,
        name: data.name,
        asset_type: data.asset_type,
        category_id: data.category_id,
        manufacturer: data.manufacturer,
        model: data.model,
        serial_number: data.serial_number,
        year_of_manufacture: data.year_of_manufacture,
        purchase_price: data.purchase_price,
        purchase_date: data.purchase_date,
        depreciation_method: data.depreciation_method,
        depreciation_years: data.depreciation_years,
        salvage_value: data.salvage_value,
        warranty_start_date: data.warranty_start_date,
        warranty_months: data.warranty_months,
        warranty_provider: data.warranty_provider,
        department_id: data.department_id,
        location: data.location,
        status: data.status,
        notes: data.notes,
      };
      createMutation.mutate(createData);
    }
  };

  if (assetLoading) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading asset data...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-background">
        <div className="border-b bg-card">
          <div className="container mx-auto px-4 py-6">
            <div>
              <h1 className="text-2xl font-bold">
                {isEditMode ? "Edit Asset" : "Create New Asset"}
              </h1>
              <p className="text-muted-foreground">
                {isEditMode
                  ? "Update asset information"
                  : "Fill in the asset details"}
              </p>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-4 py-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Basic Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Basic Information</CardTitle>
                  <CardDescription>
                    Enter the basic details of the asset
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-4">
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="code"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Asset Code *</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="AST-001"
                              {...field}
                              disabled={isEditMode}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Asset Name *</FormLabel>
                          <FormControl>
                            <Input placeholder="Dell Laptop" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="asset_type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Asset Type *</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                            disabled={isEditMode}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select asset type" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value={AssetType.FIXED_ASSET}>
                                Fixed Asset
                              </SelectItem>
                              <SelectItem value={AssetType.TOOL_EQUIPMENT}>
                                Tool/Equipment
                              </SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="category_id"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Category *</FormLabel>
                          <Select
                            onValueChange={(value) =>
                              field.onChange(Number(value))
                            }
                            value={field.value?.toString()}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select category" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {categories?.map((category) => (
                                <SelectItem
                                  key={category.id}
                                  value={category.id.toString()}
                                >
                                  {category.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="status"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Status *</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select status" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value={AssetStatus.NEW}>
                                New
                              </SelectItem>
                              <SelectItem value={AssetStatus.IN_USE}>
                                In Use
                              </SelectItem>
                              <SelectItem value={AssetStatus.UNDER_MAINTENANCE}>
                                Under Maintenance
                              </SelectItem>
                              <SelectItem value={AssetStatus.DAMAGED}>
                                Damaged
                              </SelectItem>
                              <SelectItem value={AssetStatus.DISPOSED}>
                                Disposed
                              </SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="location"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Location</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Building A, Floor 3"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <FormField
                      control={form.control}
                      name="manufacturer"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Manufacturer</FormLabel>
                          <FormControl>
                            <Input placeholder="Dell" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="model"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Model</FormLabel>
                          <FormControl>
                            <Input placeholder="Latitude 7490" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="serial_number"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Serial Number</FormLabel>
                          <FormControl>
                            <Input placeholder="SN123456789" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <FormField
                    control={form.control}
                    name="year_of_manufacture"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Year of Manufacture</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="2023"
                            {...field}
                            onChange={(e) =>
                              field.onChange(Number(e.target.value))
                            }
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </CardContent>
              </Card>

              {/* Financial Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Financial Information</CardTitle>
                  <CardDescription>
                    Enter the financial details of the asset
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-4">
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="purchase_price"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Purchase Price (VND) *</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              placeholder="10000000"
                              {...field}
                              onChange={(e) =>
                                field.onChange(Number(e.target.value))
                              }
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="purchase_date"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Purchase Date *</FormLabel>
                          <FormControl>
                            <Input type="date" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <FormField
                      control={form.control}
                      name="depreciation_method"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Depreciation Method</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            value={field.value}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select method" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="straight_line">
                                Straight Line
                              </SelectItem>
                              <SelectItem value="declining_balance">
                                Declining Balance
                              </SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="depreciation_years"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Depreciation Years</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              placeholder="5"
                              {...field}
                              onChange={(e) =>
                                field.onChange(Number(e.target.value))
                              }
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="salvage_value"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Salvage Value (VND)</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              placeholder="1000000"
                              {...field}
                              onChange={(e) =>
                                field.onChange(Number(e.target.value))
                              }
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Warranty Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Warranty Information</CardTitle>
                  <CardDescription>
                    Enter the warranty details if applicable
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-4">
                  <div className="grid grid-cols-3 gap-4">
                    <FormField
                      control={form.control}
                      name="warranty_start_date"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Warranty Start Date</FormLabel>
                          <FormControl>
                            <Input type="date" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="warranty_months"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Warranty Period (months)</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              placeholder="12"
                              {...field}
                              onChange={(e) =>
                                field.onChange(Number(e.target.value))
                              }
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="warranty_provider"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Warranty Provider</FormLabel>
                          <FormControl>
                            <Input placeholder="Dell Vietnam" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Additional Notes */}
              <Card>
                <CardHeader>
                  <CardTitle>Additional Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <FormField
                    control={form.control}
                    name="notes"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Notes</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Enter any additional notes about this asset..."
                            rows={4}
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </CardContent>
              </Card>

              {/* Form Actions */}
              <div className="flex justify-end gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate(-1)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={
                    createMutation.isPending || updateMutation.isPending
                  }
                >
                  <Save className="mr-2 h-4 w-4" />
                  {isEditMode ? "Update Asset" : "Create Asset"}
                </Button>
              </div>
            </form>
          </Form>
        </div>
      </div>
    </AppLayout>
  );
}
