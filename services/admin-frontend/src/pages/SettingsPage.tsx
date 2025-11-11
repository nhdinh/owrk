import { useState, useEffect } from 'react';
import { adminAPI } from '../lib/api';
import { ModuleSetting, ModuleSettingCreate } from '../types/settings';
import { formatDate, getModuleBadgeColor } from '../lib/utils';


export default function SettingsPage() {
  const [settings, setSettings] = useState<ModuleSetting[]>([]);
  const [loading, setLoading] = useState(true);
  const [moduleFilter, setModuleFilter] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedSetting, setSelectedSetting] = useState<ModuleSetting | null>(null);
  const [formData, setFormData] = useState<ModuleSettingCreate>({
    module_name: '',
    setting_key: '',
    setting_value: '',
    setting_type: 'STRING',
    display_name: '',
    description: '',
    is_public: true,
    is_editable: true,
  });

  useEffect(() => {
    loadSettings();
  }, [moduleFilter]);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.settings.list({
        module_name: moduleFilter || undefined,
      });
      setSettings(response.data);
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await adminAPI.settings.create(formData);
      await loadSettings();
      setShowCreateModal(false);
      resetForm();
    } catch (error) {
      console.error('Failed to create setting:', error);
    }
  };

  const handleUpdate = async () => {
    if (!selectedSetting) return;
    try {
      await adminAPI.settings.update(selectedSetting.id, {
        setting_value: formData.setting_value,
        description: formData.description,
        is_public: formData.is_public,
        is_editable: formData.is_editable,
      });
      await loadSettings();
      setShowEditModal(false);
      setSelectedSetting(null);
      resetForm();
    } catch (error) {
      console.error('Failed to update setting:', error);
    }
  };

  const handleDelete = async () => {
    if (!selectedSetting) return;
    try {
      await adminAPI.settings.delete(selectedSetting.id);
      await loadSettings();
      setShowDeleteModal(false);
      setSelectedSetting(null);
    } catch (error) {
      console.error('Failed to delete setting:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      module_name: '',
      setting_key: '',
      setting_value: '',
      setting_type: 'STRING',
      display_name: '',
      description: '',
      is_public: true,
      is_editable: true,
    });
  };

  const openEditModal = (setting: ModuleSetting) => {
    setSelectedSetting(setting);
    setFormData({
      module_name: setting.module_name,
      setting_key: setting.setting_key,
      setting_value: setting.setting_value,
      setting_type: setting.setting_type,
      display_name: setting.display_name,
      description: setting.description || '',
      is_public: setting.is_public,
      is_editable: setting.is_editable,
    });
    setShowEditModal(true);
  };

  const uniqueModules = Array.from(new Set(settings.map((s) => s.module_name)));

  return (
    <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Module Settings</h1>
              <p className="mt-2 text-gray-600">Configure settings for all modules</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Setting
            </button>
          </div>
  
          {/* Filter */}
          <div className="bg-white p-4 rounded-lg border border-gray-200 mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Module</label>
            <select
              value={moduleFilter}
              onChange={(e) => setModuleFilter(e.target.value)}
              className="w-full md:w-64 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Modules</option>
              {uniqueModules.map((module) => (
                <option key={module} value={module}>
                  {module}
                </option>
              ))}
            </select>
          </div>
  
          {/* Settings Table */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            {loading ? (
              <div className="p-8 text-center text-gray-500">Loading...</div>
            ) : settings.length === 0 ? (
              <div className="p-8 text-center text-gray-500">No settings found</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Module
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Key
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Value
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Updated
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {settings.map((setting) => (
                      <tr key={setting.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full ${getModuleBadgeColor(setting.module_name)}`}>
                            {setting.module_name}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">{setting.display_name || setting.setting_key}</div>
                          {setting.description && (
                            <div className="text-xs text-gray-500">{setting.description}</div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-sm text-gray-900 font-mono">{setting.setting_value}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-800">
                            {setting.setting_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(setting.updated_at)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => openEditModal(setting)}
                            className="text-blue-600 hover:text-blue-900 mr-4"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => {
                              setSelectedSetting(setting);
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
  
          {/* Create Modal */}
          {showCreateModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-lg max-w-2xl w-full p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Setting</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Module Name</label>
                    <input
                      type="text"
                      value={formData.module_name}
                      onChange={(e) => setFormData({ ...formData, module_name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., auth, asset, procurement"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Setting Key</label>
                    <input
                      type="text"
                      value={formData.setting_key}
                      onChange={(e) => setFormData({ ...formData, setting_key: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., max_login_attempts"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Display Name</label>
                    <input
                      type="text"
                      value={formData.display_name}
                      onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Maximum Login Attempts"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Value</label>
                    <input
                      type="text"
                      value={formData.setting_value}
                      onChange={(e) => setFormData({ ...formData, setting_value: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Data Type</label>
                    <select
                      value={formData.setting_type}
                      onChange={(e) => setFormData({ ...formData, setting_type: e.target.value as any })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="STRING">String</option>
                      <option value="INTEGER">Integer</option>
                      <option value="BOOLEAN">Boolean</option>
                      <option value="JSON">JSON</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={3}
                    />
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_public}
                      onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 text-sm text-gray-700">Public setting</label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_editable}
                      onChange={(e) => setFormData({ ...formData, is_editable: e.target.checked })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 text-sm text-gray-700">Editable</label>
                  </div>
                </div>
                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setShowCreateModal(false);
                      resetForm();
                    }}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreate}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Create
                  </button>
                </div>
              </div>
            </div>
          )}
  
          {/* Edit Modal */}
          {showEditModal && selectedSetting && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-lg max-w-2xl w-full p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Edit Setting</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Module</label>
                    <input
                      type="text"
                      value={selectedSetting.module_name}
                      disabled
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Setting Key</label>
                    <input
                      type="text"
                      value={selectedSetting.setting_key}
                      disabled
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Value</label>
                    <input
                      type="text"
                      value={formData.setting_value}
                      onChange={(e) => setFormData({ ...formData, setting_value: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={3}
                    />
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_public}
                      onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 text-sm text-gray-700">Public setting</label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_editable}
                      onChange={(e) => setFormData({ ...formData, is_editable: e.target.checked })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 text-sm text-gray-700">Editable</label>
                  </div>
                </div>
                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setShowEditModal(false);
                      setSelectedSetting(null);
                      resetForm();
                    }}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleUpdate}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Update
                  </button>
                </div>
              </div>
            </div>
          )}
  
          {/* Delete Modal */}
          {showDeleteModal && selectedSetting && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-lg max-w-md w-full p-6">
                <h3 className="text-lg font-semibold text-red-600 mb-4">Delete Setting</h3>
                <p className="text-gray-600 mb-6">
                  Are you sure you want to delete the setting <strong>{selectedSetting.setting_key}</strong> from module{' '}
                  <strong>{selectedSetting.module_name}</strong>?
                </p>
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setShowDeleteModal(false);
                      setSelectedSetting(null);
                    }}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDelete}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
  );
}
