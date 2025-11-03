import { Home, Users, Package, Shield, LogOut, Menu, X } from 'lucide-react';
import { useState } from 'react';

interface NavItem {
  name: string;
  href: string;
  icon: any;
  current?: boolean;
}

interface AppSidebarProps {
  currentService?: 'dashboard' | 'auth' | 'assets';
  userName?: string;
  userEmail?: string;
  onLogout?: () => void;
}

export function AppSidebar({
  currentService = 'dashboard',
  userName = 'User',
  userEmail = 'user@example.com',
  onLogout,
}: AppSidebarProps) {
  const [isOpen, setIsOpen] = useState(false);

  const navigation: NavItem[] = [
    { name: 'Dashboard', href: '/dashboard/', icon: Home, current: currentService === 'dashboard' },
    { name: 'Users & Roles', href: '/auth/', icon: Users, current: currentService === 'auth' },
    { name: 'Assets', href: '/assets/', icon: Package, current: currentService === 'assets' },
  ];

  const toggleSidebar = () => setIsOpen(!isOpen);

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={toggleSidebar}
          className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
        >
          <span className="sr-only">Open sidebar</span>
          {isOpen ? (
            <X className="block h-6 w-6" aria-hidden="true" />
          ) : (
            <Menu className="block h-6 w-6" aria-hidden="true" />
          )}
        </button>
      </div>

      {/* Sidebar overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-40 lg:hidden"
          onClick={toggleSidebar}
        ></div>
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed inset-y-0 left-0 z-40 w-64 bg-gray-900 transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:inset-0
        `}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-4 bg-gray-800">
            <Shield className="h-8 w-8 text-blue-500" />
            <span className="ml-2 text-xl font-bold text-white">Asset Mgmt</span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.name}
                  href={item.href}
                  className={`
                    group flex items-center px-2 py-2 text-sm font-medium rounded-md
                    ${
                      item.current
                        ? 'bg-gray-800 text-white'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    }
                  `}
                  onClick={() => setIsOpen(false)}
                >
                  <Icon
                    className={`
                      mr-3 h-6 w-6 flex-shrink-0
                      ${item.current ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-300'}
                    `}
                    aria-hidden="true"
                  />
                  {item.name}
                </a>
              );
            })}
          </nav>

          {/* User section */}
          <div className="flex-shrink-0 border-t border-gray-700 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-gray-700 flex items-center justify-center">
                  <Users className="h-6 w-6 text-gray-300" />
                </div>
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-white truncate">{userName}</p>
                <p className="text-xs font-medium text-gray-400 truncate">{userEmail}</p>
              </div>
              {onLogout && (
                <button
                  onClick={onLogout}
                  className="ml-auto flex-shrink-0 p-1 rounded-full text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800"
                  title="Logout"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
