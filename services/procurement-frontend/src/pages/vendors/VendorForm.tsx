import { useNavigate, useParams } from 'react-router-dom';
import { useVendor, useCreateVendor, useUpdateVendor } from '@/hooks/useVendors';
import { VendorStatus } from '@/types';
import { useState, useEffect } from 'react';

export default function VendorForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const { data: existingVendor } = useVendor(id!);
  const createMutation = useCreateVendor();
  const updateMutation = useUpdateVendor();

  const [formData, setFormData] = useState({
    name: '',
    contact_person: '',
    email: '',
    phone: '',
    address: '',
    tax_id: '',
    status: VendorStatus.ACTIVE,
    rating: 0,
    notes: '',
  });

  useEffect(() => {
    if (existingVendor) {
      setFormData({
        name: existingVendor.name,
        contact_person: existingVendor.contact_person || '',
        email: existingVendor.email || '',
        phone: existingVendor.phone || '',
        address: existingVendor.address || '',
        tax_id: existingVendor.tax_id || '',
        status: existingVendor.status,
        rating: existingVendor.rating || 0,
        notes: existingVendor.notes || '',
      });
    }
  }, [existingVendor]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Prepare data - remove empty strings and convert rating
    const submitData: any = {
      name: formData.name,
      status: formData.status,
    };

    if (formData.contact_person) submitData.contact_person = formData.contact_person;
    if (formData.email) submitData.email = formData.email;
    if (formData.phone) submitData.phone = formData.phone;
    if (formData.address) submitData.address = formData.address;
    if (formData.tax_id) submitData.tax_id = formData.tax_id;
    if (formData.rating > 0) submitData.rating = formData.rating;
    if (formData.notes) submitData.notes = formData.notes;

    try {
      if (isEdit && id) {
        await updateMutation.mutateAsync({
          id: parseInt(id),
          data: submitData,
        });
      } else {
        await createMutation.mutateAsync(submitData);
      }
      navigate('/vendors');
    } catch (error) {
      console.error('Failed to save vendor:', error);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">
          {isEdit ? 'Edit Vendor' : 'Create Vendor'}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-card rounded-lg border p-6">
            <h2 className="text-xl font-semibold mb-4">Basic Information</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Vendor Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Contact Person</label>
                  <input
                    type="text"
                    value={formData.contact_person}
                    onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Phone</label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Tax ID</label>
                  <input
                    type="text"
                    value={formData.tax_id}
                    onChange={(e) => setFormData({ ...formData, tax_id: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Address</label>
                <textarea
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Status *</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as VendorStatus })}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    {Object.values(VendorStatus).map((status) => (
                      <option key={status} value={status}>{status}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Rating (0-5)</label>
                  <input
                    type="number"
                    value={formData.rating}
                    onChange={(e) => setFormData({ ...formData, rating: parseFloat(e.target.value) || 0 })}
                    min="0"
                    max="5"
                    step="0.1"
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <p className="text-xs text-muted-foreground mt-1">Leave at 0 if not rated yet</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  rows={4}
                  placeholder="Additional notes about this vendor..."
                />
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
            >
              {isEdit ? 'Update' : 'Create'} Vendor
            </button>
            <button
              type="button"
              onClick={() => navigate('/vendors')}
              className="px-6 py-2 border rounded-lg hover:bg-muted"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
