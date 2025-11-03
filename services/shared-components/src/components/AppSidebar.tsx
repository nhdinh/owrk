import {
  Home,
  Users,
  Package,
  Shield,
  LogOut,
  Menu,
  X,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  User,
  Key,
  FolderTree,
  UserCheck,
  Wrench,
  HandCoins,
  Trash,
} from 'lucide-react';
import { useState } from 'react';
import yaml from 'js-yaml';
import navigationConfig from '../config/navigation.yaml?raw';
import { useAuth } from '../contexts/AuthContext';

// Icon mapping
const iconMap: Record<string, any> = {
  Home,
  Users,
  Package,
  Shield,
  ShieldCheck,
  User,
  Key,
  FolderTree,
  UserCheck,
  Wrench,
  HandCoins,
  Trash,
};

interface SubMenuItem {
  name: string;
  href: string;
  icon: string;
  description?: string;
}

interface NavItem {
  name: string;
  href: string;
  icon: string;
  service?: string;
  description?: string;
  submenu?: SubMenuItem[];
}

interface NavigationConfig {
  navigation: NavItem[];
}

interface AppSidebarProps {
  currentService?: 'dashboard' | 'auth' | 'assets';
}

export function AppSidebar({
  currentService = 'dashboard',
}: AppSidebarProps) {
  // Use AuthContext for user state
  const { user, isLoading, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set([currentService]));

  // Parse YAML configuration
  const config = yaml.load(navigationConfig) as NavigationConfig;
  const navigation = config.navigation;

  const toggleSidebar = () => setIsOpen(!isOpen);

  const toggleExpanded = (itemName: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemName)) {
      newExpanded.delete(itemName);
    } else {
      newExpanded.add(itemName);
    }
    setExpandedItems(newExpanded);
  };

  const isCurrentPath = (href: string) => {
    if (typeof window === 'undefined') return false;

    if (href.startsWith('/auth/')) {
      return window.location.pathname.startsWith(href);
    } else {
      return window.location.pathname === href;
    }
  };

  const renderNavItem = (item: NavItem) => {
    const Icon = iconMap[item.icon] || Package;
    const hasSubmenu = item.submenu && item.submenu.length > 0;
    const isExpanded = expandedItems.has(item.service || item.name);
    const isCurrent = item.service === currentService || isCurrentPath(item.href);

    return (
      <div key={item.name} className="space-y-1">
        {/* Main menu item */}
        <div
          className={`
            group flex items-center px-2 py-2 text-sm font-medium rounded-md cursor-pointer
            ${isCurrent ? 'bg-gray-800 text-white' : 'text-gray-300 hover:bg-gray-700 hover:text-white'}
          `}
          onClick={() => {
            if (hasSubmenu) {
              toggleExpanded(item.service || item.name);
            } else {
              window.location.href = item.href;
              setIsOpen(false);
            }
          }}
        >
          <Icon
            className={`
              mr-3 h-6 w-6 flex-shrink-0
              ${isCurrent ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-300'}
            `}
            aria-hidden="true"
          />
          <span className="flex-1">{item.name}</span>
          {hasSubmenu && (
            isExpanded ? (
              <ChevronDown className="h-4 w-4 text-gray-400" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-400" />
            )
          )}
        </div>

        {/* Submenu items */}
        {hasSubmenu && isExpanded && (
          <div className="ml-6 space-y-1">
            {item.submenu!.map((subItem) => {
              const SubIcon = iconMap[subItem.icon] || Package;
              const isSubCurrent = isCurrentPath(subItem.href);

              return (
                <a
                  key={subItem.name}
                  href={subItem.href}
                  className={`
                    group flex items-center px-2 py-1.5 text-xs font-medium rounded-md
                    ${isSubCurrent
                      ? 'bg-gray-700 text-white'
                      : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                    }
                  `}
                  onClick={() => setIsOpen(false)}
                  title={subItem.description}
                >
                  <SubIcon
                    className={`
                      mr-2 h-4 w-4 flex-shrink-0
                      ${isSubCurrent ? 'text-blue-400' : 'text-gray-500 group-hover:text-gray-400'}
                    `}
                    aria-hidden="true"
                  />
                  {subItem.name}
                </a>
              );
            })}
          </div>
        )}
      </div>
    );
  };

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
            {navigation.map(renderNavItem)}
          </nav>

          {/* User section */}
          <div className="flex-shrink-0 border-t border-gray-700 p-4">
            {isLoading ? (
              <div className="flex items-center justify-center py-2">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
              </div>
            ) : user ? (
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center">
                    <span className="text-white font-semibold text-sm">
                      {user.full_name
                        .split(' ')
                        .map((n) => n[0])
                        .join('')
                        .toUpperCase()
                        .slice(0, 2)}
                    </span>
                  </div>
                </div>
                <div className="ml-3 flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate" title={user.full_name}>
                    {user.full_name}
                  </p>
                  <p className="text-xs font-medium text-gray-400 truncate" title={user.email}>
                    {user.email}
                  </p>
                  {user.role && (
                    <p className="text-xs text-blue-400 truncate" title={user.role.display_name}>
                      {user.role.display_name}
                    </p>
                  )}
                </div>
                <button
                  onClick={logout}
                  className="ml-auto flex-shrink-0 p-1 rounded-full text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800"
                  title="Logout"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <a
                  href="/auth/login"
                  className="text-sm text-blue-400 hover:text-blue-300 font-medium"
                >
                  Sign In
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
