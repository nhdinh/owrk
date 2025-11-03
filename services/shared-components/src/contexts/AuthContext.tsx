import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// User interface matching the API response
export interface User {
  id: number;
  email: string;
  full_name: string;
  role?: {
    name: string;
    display_name: string;
  };
}

// AuthContext interface
export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (accessToken: string, refreshToken: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// AuthProvider props
interface AuthProviderProps {
  children: ReactNode;
  apiBaseUrl?: string;
}

// AuthProvider component
export function AuthProvider({
  children,
  apiBaseUrl = 'http://localhost:8000'
}: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch user from API
  const fetchUser = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        // Token invalid or expired
        console.warn('Token validation failed, clearing tokens');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
      }
    } catch (error) {
      console.error('Failed to fetch user:', error);
      // Don't clear tokens on network error, might be temporary
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch user on mount
  useEffect(() => {
    fetchUser();
  }, []);

  // Login function - stores tokens and fetches user
  const login = async (accessToken: string, refreshToken: string) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    await fetchUser();
  };

  // Logout function - clears tokens and redirects
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    window.location.href = '/auth/login';
  };

  // Refresh user data
  const refreshUser = async () => {
    await fetchUser();
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// useAuth hook
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
