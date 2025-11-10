import { AppLayout } from '../components/AppLayout';
import { useState, useEffect } from 'react';
import { adminAPI } from '../lib/api';
import { TrashItem, TrashStats } from '../types/trash';
import { formatDate, formatRelativeTime, getModuleBadgeColor } from '../lib/utils';


export default function TrashPage() {
  const [items, setItems] = useState<TrashItem[]>([]);
  const [stats, setStats] = useState<TrashStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    module: '',
    type: '',
    search: '',
  });
  const [selectedItem, setSelectedItem] = useState<TrashItem | null>(null);
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [itemsRes, statsRes] = await Promise.all([
        adminAPI.trash.list({
          module_name: filters.module || undefined,
          resource_type: filters.type || undefined,
          search: filters.search || undefined,
        }),
        adminAPI.trash.stats(),
      ]);
      setItems(itemsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Failed to load trash data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (item: TrashItem) => {
    try {
      await adminAPI.trash.restore(item.id, {
        reason: 'Restored by admin',
      });
      await loadData();
      setShowRestoreModal(false);
      setSelectedItem(null);
    } catch (error) {
      console.error('Failed to restore item:', error);
    }
  };

  const handlePermanentDelete = async (item: TrashItem) => {
    try {
      await adminAPI.trash.permanentDelete(item.id, {
        reason: 'Permanently deleted by admin',
      });
      await loadData();
      setShowDeleteModal(false);
      setSelectedItem(null);
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  return (
    <AppLayout>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Trash Management</h1>
            <p className="mt-2 text-gray-600">Manage deleted items across all modules</p>
          </div>
  
          {/* Statistics Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-sm text-gray-600">Total Items</div>
                <div className="mt-1 text-2xl font-bold text-gray-900">{stats.total_items}</div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-sm text-gray-600">Restorable</div>
                <div className="mt-1 text-2xl font-bold text-green-600">{stats.restorable_count}</div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-sm text-gray-600">Scheduled for Deletion</div>
                <div className="mt-1 text-2xl font-bold text-red-600">{stats.scheduled_for_deletion}</div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-sm text-gray-600">Modules</div>
                <div className="mt-1 text-2xl font-bold text-blue-600">
                  {Object.keys(stats.by_module).length}
                </div>
              </div>
            </div>
          )}
  
          {/* Filters */}
          <div className="bg-white p-4 rounded-lg border border-gray-200 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Module</label>
                <select
                  value={filters.module}
                  onChange={(e) => setFilters({ ...filters, module: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Modules</option>
                  {stats &&
                    Object.keys(stats.by_module).map((module) => (
                      <option key={module} value={module}>
                        {module} ({stats.by_module[module]})
                      </option>
                    ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={filters.type}
                  onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Types</option>
                  {stats &&
                    Object.keys(stats.by_type).map((type) => (
                      <option key={type} value={type}>
                        {type} ({stats.by_type[type]})
                      </option>
                    ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
                <input
                  type="text"
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  placeholder="Search by name..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
  
          {/* Trash Items Table */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            {loading ? (
              <div className="p-8 text-center text-gray-500">Loading...</div>
            ) : items.length === 0 ? (
              <div className="p-8 text-center text-gray-500">No items in trash</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Item
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Module
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Deleted
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {items.map((item) => (
                      <tr key={item.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{item.resource_name}</div>
                          <div className="text-sm text-gray-500">ID: {item.resource_id}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full ${getModuleBadgeColor(item.module_name)}`}>
                            {item.module_name}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {item.resource_type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{formatRelativeTime(item.deleted_at)}</div>
                          <div className="text-xs text-gray-500">{formatDate(item.deleted_at)}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {item.is_restorable ? (
                            <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                              Restorable
                            </span>
                          ) : (
                            <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">
                              Permanent
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          {item.is_restorable && (
                            <button
                              onClick={() => {
                                setSelectedItem(item);
                                setShowRestoreModal(true);
                              }}
                              className="text-blue-600 hover:text-blue-900 mr-4"
                            >
                              Restore
                            </button>
                          )}
                          <button
                            onClick={() => {
                              setSelectedItem(item);
                              setShowDeleteModal(true);
                            }}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
  
          {/* Restore Modal */}
          {showRestoreModal && selectedItem && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-lg max-w-md w-full p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Restore Item</h3>
                <p className="text-gray-600 mb-6">
                  Are you sure you want to restore <strong>{selectedItem.resource_name}</strong>?
                </p>
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setShowRestoreModal(false);
                      setSelectedItem(null);
                    }}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleRestore(selectedItem)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Restore
                  </button>
                </div>
              </div>
            </div>
          )}
  
          {/* Delete Modal */}
          {showDeleteModal && selectedItem && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-lg max-w-md w-full p-6">
                <h3 className="text-lg font-semibold text-red-600 mb-4">Permanent Delete</h3>
                <p className="text-gray-600 mb-6">
                  Are you sure you want to <strong>permanently delete</strong>{' '}
                  <strong>{selectedItem.resource_name}</strong>? This action cannot be undone.
                </p>
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setShowDeleteModal(false);
                      setSelectedItem(null);
                    }}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handlePermanentDelete(selectedItem)}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    Delete Permanently
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
