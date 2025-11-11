import {
  ShieldCheck,
  Trash2,
  Settings,
  PackageOpen,
  Logs,
  BookOpen,
  BadgeInfo,
} from "lucide-react";

export default function Dashboard() {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="px-4 py-4 lg:px-8">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <ShieldCheck className="h-6 w-6" />
              Admin Dashboard
            </h1>
            <p className="text-sm text-muted-foreground">
              System Administration & Configuration
            </p>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto px-4 py-8 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Trash Management */}
            <a
              href="/admin/trash"
              className="block p-6 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all"
            >
              <div className="flex items-center mb-4">
                <div className="p-2 bg-red-100 rounded-lg">
                  <Trash2 className="w-6 h-6 text-red-600" />
                </div>
                <h2 className="ml-3 text-xl font-semibold text-gray-900">
                  Trash
                </h2>
              </div>
              <p className="text-gray-600">
                Manage deleted items across all modules
              </p>
              <div className="mt-4 text-sm text-blue-600 font-medium">
                View Trash →
              </div>
            </a>

            {/* Module Settings */}
            <a
              href="/admin/settings"
              className="block p-6 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all"
            >
              <div className="flex items-center mb-4">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Settings className="w-6 h-6 text-blue-600" />
                </div>
                <h2 className="ml-3 text-xl font-semibold text-gray-900">
                  Settings
                </h2>
              </div>
              <p className="text-gray-600">
                Configure module settings and preferences
              </p>
              <div className="mt-4 text-sm text-blue-600 font-medium">
                Manage Settings →
              </div>
            </a>

            {/* System Modules */}
            <a
              href="/admin/modules"
              className="block p-6 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all"
            >
              <div className="flex items-center mb-4">
                <div className="p-2 bg-green-100 rounded-lg">
                  <PackageOpen className="w-6 h-6 text-green-600" />
                </div>
                <h2 className="ml-3 text-xl font-semibold text-gray-900">
                  Modules
                </h2>
              </div>
              <p className="text-gray-600">View and manage system modules</p>
              <div className="mt-4 text-sm text-blue-600 font-medium">
                View Modules →
              </div>
            </a>

            {/* Audit Logs */}
            <a
              href="/admin/audit-logs"
              className="block p-6 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all"
            >
              <div className="flex items-center mb-4">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Logs className="w-6 h-6 text-purple-600" />
                </div>
                <h2 className="ml-3 text-xl font-semibold text-gray-900">
                  Audit Logs
                </h2>
              </div>
              <p className="text-gray-600">
                View system audit trail and activity logs
              </p>
              <div className="mt-4 text-sm text-blue-600 font-medium">
                View Logs →
              </div>
            </a>

            {/* API Documentation */}
            <a
              href="http://localhost:8005/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="block p-6 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all"
            >
              <div className="flex items-center mb-4">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <BookOpen className="w-6 h-6 text-orange-600" />
                </div>
                <h2 className="ml-3 text-xl font-semibold text-gray-900">
                  API Docs
                </h2>
              </div>
              <p className="text-gray-600">
                View Admin API documentation (Swagger)
              </p>
              <div className="mt-4 text-sm text-blue-600 font-medium">
                Open API Docs ↗
              </div>
            </a>

            {/* Documentation */}
            <div className="block p-6 bg-white rounded-lg border border-gray-200">
              <div className="flex items-center mb-4">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <BadgeInfo className="w-6 h-6 text-gray-600" />
                </div>
                <h2 className="ml-3 text-xl font-semibold text-gray-900">
                  Documentation
                </h2>
              </div>
              <p className="text-gray-600 mb-3">
                Admin module documentation and guides
              </p>
              <ul className="space-y-2 text-sm">
                <li>
                  <a
                    href="https://github.com/yourusername/officework/blob/main/services/admin-api/README.md"
                    className="text-blue-600 hover:underline"
                  >
                    Admin API README
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/yourusername/officework/blob/main/services/admin-api/TRASH_FEATURE_GUIDE.md"
                    className="text-blue-600 hover:underline"
                  >
                    Trash Feature Guide
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/yourusername/officework/blob/main/ADMIN_MODULE_COMPLETE.md"
                    className="text-blue-600 hover:underline"
                  >
                    Implementation Summary
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Status Cards */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-sm text-gray-600">Admin API</div>
              <div className="mt-1 flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                <div className="text-lg font-semibold">Running</div>
              </div>
              <div className="mt-1 text-xs text-gray-500">Port 8005</div>
            </div>

            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-sm text-gray-600">Endpoints</div>
              <div className="mt-1 text-2xl font-bold text-gray-900">26</div>
              <div className="mt-1 text-xs text-gray-500">
                9 Settings + 17 Trash
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-sm text-gray-600">Database</div>
              <div className="mt-1 text-lg font-semibold">admin_db</div>
              <div className="mt-1 text-xs text-gray-500">6 tables</div>
            </div>

            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-sm text-gray-600">Scheduler</div>
              <div className="mt-1 flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                <div className="text-lg font-semibold">Active</div>
              </div>
              <div className="mt-1 text-xs text-gray-500">
                Trash cleanup running
              </div>
            </div>
          </div>

          {/* Notice */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-blue-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">
                  Admin Module Status
                </h3>
                <div className="mt-2 text-sm text-blue-700">
                  <p>
                    Backend API is fully functional. Frontend UI pages are under
                    development. Use the API documentation link above to explore
                    all available endpoints.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
  );
}
