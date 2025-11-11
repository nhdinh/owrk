import { useParams, Link, useNavigate } from 'react-router-dom';
import { useVendor, useDeleteVendor } from '@/hooks/useVendors';
import { VendorStatus } from '@/types';

export default function VendorDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: vendor, isLoading, error } = useVendor(id!);
  const deleteMutation = useDeleteVendor();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !vendor) {
    return (
      <div className="p-8">
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg">
          Error loading vendor
        </div>
      </div>
    );
  }

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this vendor?')) {
      try {
        await deleteMutation.mutateAsync(vendor.id);
        navigate('/vendors');
      } catch (error) {
        console.error('Failed to delete:', error);
      }
    }
  };

  return (
    <div className="p-8">
      <div className="mb-6">
        <Link to="/vendors" className="text-primary hover:underline text-sm">
          ← Back to Vendors
        </Link>
      </div>

      <div className="bg-card rounded-lg border p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl font-bold">{vendor.name}</h1>
            <p className="text-muted-foreground mt-1">{vendor.vendor_code}</p>
          </div>
          <div className="flex gap-2">
            <Link
              to={`/vendors/${vendor.id}/edit`}
              className="px-4 py-2 border rounded-lg hover:bg-muted"
            >
              Edit
            </Link>
            <button
              onClick={handleDelete}
              className="px-4 py-2 border border-destructive text-destructive rounded-lg hover:bg-destructive/10"
            >
              Delete
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <p className="text-sm text-muted-foreground">Vendor Code</p>
            <p className="font-medium">{vendor.vendor_code}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Status</p>
            <span className={`px-2 py-1 text-xs rounded-full ${
              vendor.status === VendorStatus.ACTIVE ? 'bg-green-100 text-green-700' :
              vendor.status === VendorStatus.BLACKLISTED ? 'bg-red-100 text-red-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {vendor.status}
            </span>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Contact Person</p>
            <p className="font-medium">{vendor.contact_person || '-'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Rating</p>
            {vendor.rating ? (
              <div className="flex items-center gap-1">
                <span className="text-yellow-500 text-lg">★</span>
                <span className="font-medium">{vendor.rating.toFixed(1)}</span>
              </div>
            ) : (
              <p className="font-medium">-</p>
            )}
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Email</p>
            <p className="font-medium">{vendor.email || '-'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Phone</p>
            <p className="font-medium">{vendor.phone || '-'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Tax ID</p>
            <p className="font-medium">{vendor.tax_id || '-'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Created At</p>
            <p className="font-medium">{new Date(vendor.created_at).toLocaleDateString()}</p>
          </div>
        </div>

        {vendor.address && (
          <div className="mb-6">
            <p className="text-sm text-muted-foreground mb-2">Address</p>
            <p>{vendor.address}</p>
          </div>
        )}

        {vendor.notes && (
          <div className="mb-6">
            <p className="text-sm text-muted-foreground mb-2">Notes</p>
            <p>{vendor.notes}</p>
          </div>
        )}

        <div className="border-t pt-4">
          <p className="text-sm text-muted-foreground">
            Last Updated: {new Date(vendor.updated_at).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
}
