// @ts-ignore - Module Federation remote import
import { AppSidebar } from "shared_components/AppSidebar";
import { AppLayout } from "@/components/AppLayout";
import {ShieldCheck } from "lucide-react";

export default function Dashboard() {
  return (
    
    <AppLayout>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="container mx-auto px-4 py-4">

            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                  <ShieldCheck className="h-6 w-6" />
                  Admin Dashboard
                </h1>
                <p className="text-sm text-muted-foreground">
              System Administration & Configuration
                </p>
              </div>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Trash Management */}
          <a
            href="/admin/trash"
            className="block p-6 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all"
          >
            <div className="flex items-center mb-4">
              <div className="p-2 bg-red-100 rounded-lg">
                <svg
                  className="w-6 h-6 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
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
                <svg
                  className="w-6 h-6 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
                  />
                </svg>
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
                <svg
                  className="w-6 h-6 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
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
                <svg
                  className="w-6 h-6 text-purple-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
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
                <svg
                  className="w-6 h-6 text-orange-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                  />
                </svg>
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
                <svg
                  className="w-6 h-6 text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
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
      </div>
    </AppLayout>
  );
}
