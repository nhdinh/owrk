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
  Monitor,
} from "lucide-react";
import { useState, useEffect } from "react";
import yaml from "js-yaml";
import { useAuth } from "../contexts/AuthContext";

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
  Monitor,
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

export interface AppSidebarProps {
  currentService?:
    | "dashboard"
    | "auth"
    | "assets"
    | "procurement"
    | "maintenance"
    | "users"
    | "admin";
  user?: any;
  isLoading?: boolean;
  onLogout?: () => void;
}

export function AppSidebar({
  currentService = "dashboard",
  user: propUser,
  isLoading: propIsLoading,
  onLogout: propOnLogout,
}: AppSidebarProps) {
  // Use AuthContext for user state (fallback if not provided via props)
  const authContext = useAuth();

  // Use props if provided, otherwise fallback to AuthContext
  const user = propUser !== undefined ? propUser : authContext.user;
  const isLoading =
    propIsLoading !== undefined ? propIsLoading : authContext.isLoading;
  const logout = propOnLogout || authContext.logout;
  const [isOpen, setIsOpen] = useState(false);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(
    new Set([currentService])
  );
  const [navigation, setNavigation] = useState<NavItem[]>([]);
  const [navLoading, setNavLoading] = useState(true);

  // Fetch navigation configuration at runtime
  useEffect(() => {
    const fetchNavigation = async () => {
      try {
        // Try /shared/navigation.yaml first (API gateway path)
        let response = await fetch("/shared/navigation.yaml");

        // If not found, try /navigation.yaml (direct access)
        if (!response.ok) {
          response = await fetch("/navigation.yaml");
        }

        if (!response.ok) {
          throw new Error(
            `Failed to fetch navigation.yaml: ${response.status}`
          );
        }

        const yamlText = await response.text();
        const config = yaml.load(yamlText) as NavigationConfig;
        setNavigation(config.navigation);
      } catch (error) {
        console.error("Failed to load navigation config:", error);
        // Fallback to empty navigation
        setNavigation([]);
      } finally {
        setNavLoading(false);
      }
    };

    fetchNavigation();
  }, []);

  // Auto-expand menus when navigation is loaded and current path matches a submenu item
  useEffect(() => {
    if (navigation.length === 0) return;

    const newExpanded = new Set<string>();
    const currentPath = typeof window !== 'undefined' ? window.location.pathname : '';

    navigation.forEach((item) => {
      // Check if the current path matches the parent menu's href or any submenu item
      const parentMatches = currentPath === item.href ||
                           (item.href.endsWith('/') && currentPath.startsWith(item.href));

      // Check if any submenu item matches the current path
      const hasActiveSubmenu = item.submenu && item.submenu.length > 0 &&
        item.submenu.some((subItem) => {
          return currentPath === subItem.href ||
                 (subItem.href.length > 1 && currentPath.startsWith(subItem.href));
        });

      // Expand if parent matches or any submenu item matches
      if (parentMatches || hasActiveSubmenu) {
        newExpanded.add(item.service || item.name);
      }
    });

    setExpandedItems(newExpanded);
  }, [navigation]); // Removed currentService from dependencies

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
    if (typeof window === "undefined") return false;

    const currentPath = window.location.pathname;

    // Exact match
    if (currentPath === href) {
      return true;
    }

    // For paths ending with /, check if current path starts with it
    // e.g., href="/dashboard/" matches "/dashboard/status"
    if (href.endsWith('/') && href.length > 1) {
      return currentPath.startsWith(href);
    }

    // For paths not ending with /, check if current path starts with it followed by /
    // e.g., href="/dashboard" matches "/dashboard/status" but not "/dashboards"
    if (!href.endsWith('/') && href.length > 1) {
      return currentPath.startsWith(href + '/');
    }

    return false;
  };

  const renderNavItem = (item: NavItem) => {
    const Icon = iconMap[item.icon] || Package;
    const hasSubmenu = item.submenu && item.submenu.length > 0;
    const isExpanded = expandedItems.has(item.service || item.name);

    // Check if this item or any of its submenu items are current
    const isSubmenuActive =
      hasSubmenu &&
      item.submenu!.some((subItem) => isCurrentPath(subItem.href));

    // For parent items with submenu: only highlight if on the exact parent path, not child paths
    // For items without submenu: highlight if path matches
    let isCurrent = false;
    if (hasSubmenu) {
      // Parent menu is only "current" if we're exactly on its href (not on submenu items)
      // This prevents the parent from being highlighted when we're on a submenu item
      const currentPath = typeof window !== 'undefined' ? window.location.pathname : '';
      isCurrent = currentPath === item.href;
    } else {
      // Regular menu item without submenu - use normal path matching
      isCurrent = isCurrentPath(item.href);
    }

    return (
      <div key={item.name} className="space-y-1">
        {/* Main menu item */}
        <div
          className={`
            group flex items-center px-2 py-2 text-sm font-medium rounded-md cursor-pointer
            ${
              isCurrent
                ? "bg-gray-800 text-white"
                : "text-gray-300 hover:bg-gray-700 hover:text-white"
            }
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
              ${
                isCurrent
                  ? "text-blue-500"
                  : isSubmenuActive
                  ? "text-blue-400"
                  : "text-gray-400 group-hover:text-gray-300"
              }
            `}
            aria-hidden="true"
          />
          <span className="flex-1">{item.name}</span>
          {hasSubmenu &&
            (isExpanded ? (
              <ChevronDown className="h-4 w-4 text-gray-400" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-400" />
            ))}
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
                    ${
                      isSubCurrent
                        ? "bg-gray-700 text-white"
                        : "text-gray-400 hover:bg-gray-700 hover:text-white"
                    }
                  `}
                  onClick={() => setIsOpen(false)}
                  title={subItem.description}
                >
                  <SubIcon
                    className={`
                      mr-2 h-4 w-4 flex-shrink-0
                      ${
                        isSubCurrent
                          ? "text-blue-400"
                          : "text-gray-500 group-hover:text-gray-400"
                      }
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
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
          lg:translate-x-0 lg:static lg:inset-0
        `}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-4 bg-gray-800">
            <Shield className="h-8 w-8 text-blue-500" />
            <span className="ml-2 text-xl font-bold text-white">
              Asset Mgmt
            </span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
            {navLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
              </div>
            ) : (
              navigation.map(renderNavItem)
            )}
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
                        .split(" ")
                        .map((n: string) => n[0])
                        .join("")
                        .toUpperCase()
                        .slice(0, 2)}
                    </span>
                  </div>
                </div>
                <div className="ml-3 flex-1 min-w-0">
                  <p
                    className="text-sm font-medium text-white truncate"
                    title={user.full_name}
                  >
                    {user.full_name}
                  </p>
                  <p
                    className="text-xs font-medium text-gray-400 truncate"
                    title={user.email}
                  >
                    {user.email}
                  </p>
                  {user.role && (
                    <p
                      className="text-xs text-blue-400 truncate"
                      title={user.role.display_name}
                    >
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
