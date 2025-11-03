import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { assetAPI } from "@/lib/asset-api";
import type { Assignment, AssignmentReturnRequest } from "@/types/asset";
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
  ClipboardList,
  PackageCheck,
  Filter,
} from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";

interface ReturnFormData {
  returned_date: string;
  return_condition: string;
  return_notes: string;
}

export default function Assignments() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [returnDialogOpen, setReturnDialogOpen] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState<Assignment | null>(null);
  const [returnFormData, setReturnFormData] = useState<ReturnFormData>({
    returned_date: new Date().toISOString().split("T")[0],
    return_condition: "good",
    return_notes: "",
  });

  const {
    data: assignments,
    isLoading,
  } = useQuery({
    queryKey: ["assignments", statusFilter],
    queryFn: () => assetAPI.listAssignments(
      statusFilter !== "all" ? { status: statusFilter } : undefined
    ),
  });

  const returnMutation = useMutation({
    mutationFn: async ({ assetId, data }: { assetId: number; data: AssignmentReturnRequest }) => {
      const response = await fetch(`http://localhost:8000/api/v1/assets/${assetId}/return`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to return asset");
      }

      return response.json();
    },
    onSuccess: () => {
      toast.success("Asset returned successfully");
      setReturnDialogOpen(false);
      setSelectedAssignment(null);
      setReturnFormData({
        returned_date: new Date().toISOString().split("T")[0],
        return_condition: "good",
        return_notes: "",
      });
      queryClient.invalidateQueries({ queryKey: ["assignments"] });
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to return asset");
    },
  });

  const handleReturn = (assignment: Assignment) => {
    setSelectedAssignment(assignment);
    setReturnFormData({
      returned_date: new Date().toISOString().split("T")[0],
      return_condition: "good",
      return_notes: "",
    });
    setReturnDialogOpen(true);
  };

  const handleReturnSubmit = () => {
    if (!selectedAssignment) return;
    if (!returnFormData.returned_date || !returnFormData.return_condition) {
      toast.error("Date and condition are required");
      return;
    }
    returnMutation.mutate({
      assetId: selectedAssignment.asset_id,
      data: returnFormData,
    });
  };

  if (isLoading) {
    return (
      <AppLayout>
        <div className="min-h-screen flex items-center justify-center">
          Loading assignments...
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
                  <ClipboardList className="h-6 w-6" />
                  Asset Assignments
                </h1>
                <p className="text-sm text-muted-foreground">
                  Track and manage asset assignments
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Assignments</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="returned">Returned</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          <Card>
            <CardHeader>
              <CardTitle>All Assignments</CardTitle>
              <CardDescription>
                {assignments?.length || 0} assignments found
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!assignments || assignments.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No assignments found.
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Asset ID</TableHead>
                      <TableHead>User ID</TableHead>
                      <TableHead>Department ID</TableHead>
                      <TableHead>Assigned Date</TableHead>
                      <TableHead>Returned Date</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Condition</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {assignments.map((assignment) => (
                      <TableRow key={assignment.id}>
                        <TableCell className="font-medium">#{assignment.asset_id}</TableCell>
                        <TableCell>User #{assignment.user_id}</TableCell>
                        <TableCell>Dept #{assignment.department_id}</TableCell>
                        <TableCell>
                          {format(new Date(assignment.assigned_date), "MMM dd, yyyy")}
                        </TableCell>
                        <TableCell>
                          {assignment.returned_date
                            ? format(new Date(assignment.returned_date), "MMM dd, yyyy")
                            : "-"}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              assignment.status === "active" ? "default" : "secondary"
                            }
                          >
                            {assignment.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {assignment.return_condition ? (
                            <Badge
                              variant={
                                assignment.return_condition === "good"
                                  ? "default"
                                  : assignment.return_condition === "damaged"
                                  ? "destructive"
                                  : "secondary"
                              }
                            >
                              {assignment.return_condition}
                            </Badge>
                          ) : (
                            "-"
                          )}
                        </TableCell>
                        <TableCell className="text-right">
                          {assignment.status === "active" && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleReturn(assignment)}
                            >
                              <PackageCheck className="h-4 w-4 mr-2" />
                              Return
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </main>

        {/* Return Dialog */}
        <Dialog open={returnDialogOpen} onOpenChange={setReturnDialogOpen}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Return Asset</DialogTitle>
              <DialogDescription>
                Record the return of asset #{selectedAssignment?.asset_id}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="returned_date">Return Date *</Label>
                <Input
                  id="returned_date"
                  type="date"
                  value={returnFormData.returned_date}
                  onChange={(e) =>
                    setReturnFormData({ ...returnFormData, returned_date: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="return_condition">Condition *</Label>
                <Select
                  value={returnFormData.return_condition}
                  onValueChange={(value) =>
                    setReturnFormData({ ...returnFormData, return_condition: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select condition" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="good">Good</SelectItem>
                    <SelectItem value="fair">Fair</SelectItem>
                    <SelectItem value="damaged">Damaged</SelectItem>
                    <SelectItem value="lost">Lost</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="return_notes">Return Notes</Label>
                <Textarea
                  id="return_notes"
                  placeholder="Any notes about the return..."
                  value={returnFormData.return_notes}
                  onChange={(e) =>
                    setReturnFormData({ ...returnFormData, return_notes: e.target.value })
                  }
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setReturnDialogOpen(false)}
                disabled={returnMutation.isPending}
              >
                Cancel
              </Button>
              <Button onClick={handleReturnSubmit} disabled={returnMutation.isPending}>
                {returnMutation.isPending ? "Processing..." : "Return Asset"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
}
