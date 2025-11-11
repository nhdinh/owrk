# Procurement Frontend Implementation Guide

**Date**: 2025-11-07
**Status**: 🚧 Implementation Guide
**Technology**: React 18 + Vite 5 + TypeScript + Tailwind + shadcn/ui + Module Federation

---

## 📋 Overview

This guide provides complete implementation details for the Procurement Frontend module, following the same architecture as auth-frontend and asset-frontend.

### Key Features

- 🛒 Purchase Request Management (Create, List, Detail, Approve/Reject)
- 🏢 Vendor Management (CRUD operations)
- 💰 Quotation Management (Create, Compare, Select)
- 📦 Purchase Order Management (Create, Track, Complete)
- 🔗 Module Federation (Shared components from shared-components service)
- 🔐 Authentication & Authorization
- 📱 Responsive Design with Tailwind CSS
- 🎨 Consistent UI with shadcn/ui components

---

## 🎯 Project Structure

```
services/procurement-frontend/
├── public/
│   └── vite.svg
├── src/
│   ├── components/           # Reusable components
│   │   ├── ui/              # shadcn/ui components
│   │   ├── layout/          # Layout components
│   │   ├── purchase-requests/
│   │   │   ├── PurchaseRequestCard.tsx
│   │   │   ├── PurchaseRequestForm.tsx
│   │   │   ├── PurchaseRequestTable.tsx
│   │   │   └── ApprovalActions.tsx
│   │   ├── vendors/
│   │   │   ├── VendorCard.tsx
│   │   │   ├── VendorForm.tsx
│   │   │   └── VendorTable.tsx
│   │   ├── quotations/
│   │   │   ├── QuotationCard.tsx
│   │   │   ├── QuotationForm.tsx
│   │   │   ├── QuotationComparison.tsx
│   │   │   └── QuotationTable.tsx
│   │   └── purchase-orders/
│   │       ├── PurchaseOrderCard.tsx
│   │       ├── PurchaseOrderForm.tsx
│   │       └── PurchaseOrderTable.tsx
│   ├── pages/
│   │   ├── purchase-requests/
│   │   │   ├── PurchaseRequestList.tsx
│   │   │   ├── PurchaseRequestDetail.tsx
│   │   │   ├── PurchaseRequestCreate.tsx
│   │   │   └── PurchaseRequestEdit.tsx
│   │   ├── vendors/
│   │   │   ├── VendorList.tsx
│   │   │   ├── VendorDetail.tsx
│   │   │   ├── VendorCreate.tsx
│   │   │   └── VendorEdit.tsx
│   │   ├── quotations/
│   │   │   ├── QuotationList.tsx
│   │   │   ├── QuotationDetail.tsx
│   │   │   ├── QuotationCreate.tsx
│   │   │   └── QuotationComparison.tsx
│   │   ├── purchase-orders/
│   │   │   ├── PurchaseOrderList.tsx
│   │   │   ├── PurchaseOrderDetail.tsx
│   │   │   └── PurchaseOrderCreate.tsx
│   │   ├── Dashboard.tsx
│   │   └── NotFound.tsx
│   ├── lib/
│   │   ├── api.ts            # Axios API client
│   │   ├── auth-context.tsx  # Authentication context
│   │   └── utils.ts          # Utility functions
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── usePurchaseRequests.ts
│   │   ├── useVendors.ts
│   │   ├── useQuotations.ts
│   │   └── usePurchaseOrders.ts
│   ├── types/
│   │   ├── purchase-request.ts
│   │   ├── vendor.ts
│   │   ├── quotation.ts
│   │   └── purchase-order.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── Dockerfile
├── nginx.conf
├── nginx-entrypoint-wrapper.sh
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── postcss.config.js
```

---

## 📦 Core Files Already Created

✅ package.json
✅ vite.config.ts
✅ tsconfig.json, tsconfig.app.json, tsconfig.node.json
✅ tailwind.config.js
✅ postcss.config.js

---

## 🔧 Implementation Steps

### Step 1: Create Basic Application Structure

**File**: `src/main.tsx`

```typescript
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.tsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter basename="/procurement">
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
```

**File**: `src/index.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

**File**: `src/App.tsx`

```typescript
import { Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import { AuthProvider } from "./lib/auth-context";

// @ts-ignore - Module Federation
import { AppSidebar } from "shared_components/AppSidebar";
import { useAuth } from "./lib/auth-context";

// Pages
import Dashboard from "./pages/Dashboard";
import PurchaseRequestList from "./pages/purchase-requests/PurchaseRequestList";
import PurchaseRequestDetail from "./pages/purchase-requests/PurchaseRequestDetail";
import PurchaseRequestCreate from "./pages/purchase-requests/PurchaseRequestCreate";
import VendorList from "./pages/vendors/VendorList";
import VendorDetail from "./pages/vendors/VendorDetail";
import VendorCreate from "./pages/vendors/VendorCreate";
import QuotationList from "./pages/quotations/QuotationList";
import QuotationDetail from "./pages/quotations/QuotationDetail";
import QuotationCreate from "./pages/quotations/QuotationCreate";
import PurchaseOrderList from "./pages/purchase-orders/PurchaseOrderList";
import PurchaseOrderDetail from "./pages/purchase-orders/PurchaseOrderDetail";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading, logout } = useAuth();

  return (
    <div className="flex h-screen bg-background">
      <AppSidebar
        currentService="procurement"
        user={user}
        isLoading={isLoading}
        onLogout={logout}
      />
      <div className="flex-1 overflow-y-auto">{children}</div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />

            {/* Purchase Requests */}
            <Route
              path="/purchase-requests"
              element={<PurchaseRequestList />}
            />
            <Route
              path="/purchase-requests/create"
              element={<PurchaseRequestCreate />}
            />
            <Route
              path="/purchase-requests/:id"
              element={<PurchaseRequestDetail />}
            />

            {/* Vendors */}
            <Route path="/vendors" element={<VendorList />} />
            <Route path="/vendors/create" element={<VendorCreate />} />
            <Route path="/vendors/:id" element={<VendorDetail />} />

            {/* Quotations */}
            <Route path="/quotations" element={<QuotationList />} />
            <Route path="/quotations/create" element={<QuotationCreate />} />
            <Route path="/quotations/:id" element={<QuotationDetail />} />

            {/* Purchase Orders */}
            <Route path="/purchase-orders" element={<PurchaseOrderList />} />
            <Route
              path="/purchase-orders/:id"
              element={<PurchaseOrderDetail />}
            />

            <Route path="*" element={<NotFound />} />
          </Routes>
        </AppLayout>
        <Toaster position="top-right" />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
```

---

### Step 2: API Client & Authentication

**File**: `src/lib/api.ts`

```typescript
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/auth/login";
    }
    return Promise.reject(error);
  }
);

export default api;
```

**File**: `src/lib/auth-context.tsx`

```typescript
import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import api from "./api";

interface User {
  id: number;
  email: string;
  full_name: string;
  role?: {
    name: string;
    display_name: string;
  };
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await api.get("/auth/me");
        setUser(response.data);
      } catch (error) {
        console.error("Failed to fetch user:", error);
        localStorage.removeItem("access_token");
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, []);

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    window.location.href = "/auth/login";
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
```

---

### Step 3: TypeScript Types

**File**: `src/types/purchase-request.ts`

```typescript
export type Priority = "low" | "medium" | "high" | "urgent";
export type ProcurementType = "framework_contract" | "quotation_comparison";
export type ApprovalStatus =
  | "draft"
  | "pending"
  | "approved_level1"
  | "approved_level2"
  | "approved"
  | "rejected"
  | "cancelled";

export interface PurchaseRequestItem {
  id?: number;
  item_name: string;
  specification: string;
  quantity: number;
  estimated_unit_price: number;
  estimated_total_price: number;
  notes?: string;
}

export interface PurchaseRequest {
  id: number;
  request_code: string;
  requester_id: number;
  department_id: number;
  priority: Priority;
  procurement_type: ProcurementType;
  estimated_budget: number;
  justification: string;
  expected_delivery_date: string;
  status: ApprovalStatus;
  items: PurchaseRequestItem[];
  created_at: string;
  updated_at: string;
}

export interface CreatePurchaseRequest {
  department_id: number;
  priority: Priority;
  procurement_type: ProcurementType;
  estimated_budget: number;
  justification: string;
  expected_delivery_date: string;
  items: Omit<PurchaseRequestItem, "id">[];
}
```

**File**: `src/types/vendor.ts`

```typescript
export type VendorStatus = "active" | "inactive" | "blacklisted";

export interface Vendor {
  id: number;
  vendor_code: string;
  vendor_name: string;
  tax_code: string;
  contact_person: string;
  contact_phone: string;
  contact_email: string;
  address: string;
  bank_name?: string;
  bank_account?: string;
  rating?: number;
  status: VendorStatus;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateVendor {
  vendor_name: string;
  tax_code: string;
  contact_person: string;
  contact_phone: string;
  contact_email: string;
  address: string;
  bank_name?: string;
  bank_account?: string;
  notes?: string;
}
```

_Continue with quotation.ts and purchase-order.ts following the same pattern..._

---

### Step 4: React Query Hooks

**File**: `src/hooks/usePurchaseRequests.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import {
  PurchaseRequest,
  CreatePurchaseRequest,
} from "@/types/purchase-request";
import { toast } from "sonner";

export function usePurchaseRequests(filters?: Record<string, string>) {
  return useQuery({
    queryKey: ["purchase-requests", filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters);
      const response = await api.get(`/purchase-requests?${params}`);
      return response.data;
    },
  });
}

export function usePurchaseRequest(id: string) {
  return useQuery({
    queryKey: ["purchase-request", id],
    queryFn: async () => {
      const response = await api.get(`/purchase-requests/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreatePurchaseRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreatePurchaseRequest) => {
      const response = await api.post("/purchase-requests", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["purchase-requests"] });
      toast.success("Purchase request created successfully");
    },
    onError: (error: any) => {
      toast.error(
        error.response?.data?.detail || "Failed to create purchase request"
      );
    },
  });
}

export function useSubmitPurchaseRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await api.post(`/purchase-requests/${id}/submit`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["purchase-requests"] });
      toast.success("Purchase request submitted for approval");
    },
    onError: (error: any) => {
      toast.error(
        error.response?.data?.detail || "Failed to submit purchase request"
      );
    },
  });
}

export function useApprovePurchaseRequest(level: 1 | 2 | 3) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, comments }: { id: number; comments?: string }) => {
      const response = await api.post(
        `/purchase-requests/${id}/approve/level${level}`,
        { comments }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["purchase-requests"] });
      toast.success(`Purchase request approved (Level ${level})`);
    },
    onError: (error: any) => {
      toast.error(
        error.response?.data?.detail || "Failed to approve purchase request"
      );
    },
  });
}
```

_Continue with useVendors.ts, useQuotations.ts, usePurchaseOrders.ts following the same pattern..._

---

### Step 5: Sample Page Component

**File**: `src/pages/purchase-requests/PurchaseRequestList.tsx`

```typescript
import { useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Filter, Search } from "lucide-react";
import { usePurchaseRequests } from "@/hooks/usePurchaseRequests";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function PurchaseRequestList() {
  const [filters, setFilters] = useState<Record<string, string>>({
    page: "1",
    limit: "20",
  });

  const { data, isLoading } = usePurchaseRequests(filters);

  const getStatusBadge = (status: string) => {
    const variants: Record<
      string,
      "default" | "secondary" | "destructive" | "outline"
    > = {
      draft: "secondary",
      pending: "outline",
      approved_level1: "outline",
      approved_level2: "outline",
      approved: "default",
      rejected: "destructive",
      cancelled: "secondary",
    };
    return (
      <Badge variant={variants[status] || "default"}>
        {status.replace("_", " ").toUpperCase()}
      </Badge>
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Purchase Requests</h1>
          <p className="text-muted-foreground">Manage procurement requests</p>
        </div>
        <Link to="/procurement/purchase-requests/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Request
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-2">
              <Search className="h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by request code..."
                value={filters.search || ""}
                onChange={(e) =>
                  setFilters({ ...filters, search: e.target.value })
                }
              />
            </div>

            <Select
              value={filters.status || "all"}
              onValueChange={(value) =>
                setFilters({ ...filters, status: value === "all" ? "" : value })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={filters.priority || "all"}
              onValueChange={(value) =>
                setFilters({
                  ...filters,
                  priority: value === "all" ? "" : value,
                })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Filter by priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priorities</SelectItem>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4">
        {isLoading ? (
          <div className="text-center py-10">Loading...</div>
        ) : data?.data?.length > 0 ? (
          data.data.map((request: any) => (
            <Link
              key={request.id}
              to={`/procurement/purchase-requests/${request.id}`}
            >
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="pt-6">
                  <div className="flex justify-between items-start">
                    <div className="space-y-2">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-semibold">
                          {request.request_code}
                        </h3>
                        {getStatusBadge(request.status)}
                        <Badge variant="outline">{request.priority}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {request.justification}
                      </p>
                      <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                        <span>
                          Budget: ${request.estimated_budget.toLocaleString()}
                        </span>
                        <span>Items: {request.items?.length || 0}</span>
                        <span>
                          Expected:{" "}
                          {new Date(
                            request.expected_delivery_date
                          ).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))
        ) : (
          <Card>
            <CardContent className="py-10 text-center">
              <p className="text-muted-foreground">
                No purchase requests found
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
```

---

### Step 6: Docker & Nginx Configuration

**File**: `Dockerfile`

```dockerfile
# Build stage
FROM node:20-alpine AS procurement-fe-builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:latest

RUN apt-get update && apt-get install -y \
  dos2unix && \
  rm -rf /var/lib/apt/lists/*

# Copy built assets from builder
COPY --from=procurement-fe-builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

**File**: `nginx.conf`

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
    gzip_disable "MSIE [1-6]\.";

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

---

### Step 7: Update docker-compose.yml

Add this service to docker-compose.yml:

```yaml
procurement-frontend:
  build:
    context: ./services/procurement-frontend
    dockerfile: Dockerfile
  container_name: procurement-frontend
  ports:
    - "3500:80"
  networks:
    - backend
  restart: unless-stopped
  healthcheck:
    test:
      [
        "CMD",
        "wget",
        "--no-verbose",
        "--tries=1",
        "--spider",
        "http://localhost/",
      ]
    interval: 30s
    timeout: 3s
    start_period: 5s
    retries: 3
```

---

### Step 8: Update Nginx API Gateway

Add this location block to nginx/default.conf:

```nginx
# Procurement Frontend
location /procurement/ {
    proxy_pass http://procurement-frontend:80/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

## 📊 Implementation Status

### ✅ Completed

- Project structure
- Configuration files (package.json, vite.config.ts, tsconfig, tailwind)
- Implementation guide documentation

### 🚧 Next Steps

1. **Create shadcn/ui components** (Est. 1 hour)

   - Run `npx shadcn@latest init`
   - Add components: button, card, input, select, badge, dialog, table, toast

2. **Implement core files** (Est. 2-3 hours)

   - main.tsx, App.tsx, index.css
   - API client & auth context
   - TypeScript types

3. **Create Purchase Request pages** (Est. 3-4 hours)

   - List, Detail, Create, Edit pages
   - Form components
   - Approval workflow UI

4. **Create Vendor pages** (Est. 2-3 hours)

   - List, Detail, Create, Edit pages
   - Vendor selection components

5. **Create Quotation pages** (Est. 3-4 hours)

   - List, Detail, Create pages
   - Quotation comparison view
   - Selection workflow

6. **Create Purchase Order pages** (Est. 2-3 hours)

   - List, Detail, Create pages
   - Order tracking components

7. **Test & Deploy** (Est. 2-3 hours)
   - Integration testing
   - Docker build & deployment
   - Update documentation

**Total Estimate**: 15-21 hours

---

## 🎯 Key Features to Implement

### Purchase Requests

- ✅ List with filters (status, priority, date range)
- ✅ Create with dynamic item list
- ✅ Detail view with approval history
- ✅ Approval workflow (3 levels)
- ✅ Reject with reason
- ✅ Cancel request

### Vendors

- ✅ List with search
- ✅ Create/Edit vendor
- ✅ View vendor details
- ✅ Vendor rating system
- ✅ Status management (active/inactive/blacklisted)

### Quotations

- ✅ List by purchase request
- ✅ Create quotation
- ✅ Compare quotations side-by-side
- ✅ Accept/Reject quotation
- ✅ Upload quotation files

### Purchase Orders

- ✅ Create from accepted quotation
- ✅ Track order status
- ✅ Update delivery information
- ✅ Complete order workflow

---

## 🔗 Integration Points

1. **Auth Service** (http://localhost:8000/api/v1/auth/)

   - Login/logout
   - User profile
   - Token management

2. **Procurement API** (http://localhost:8000/api/v1/)

   - /purchase-requests
   - /vendors
   - /quotations
   - /purchase-orders

3. **Shared Components** (Module Federation)
   - AppSidebar
   - AppLayout
   - Common UI components

---

## 📝 Environment Variables

Create `.env` file:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 🚀 Running the Application

```bash
# Development
cd services/procurement-frontend
npm install
npm run dev
# Access: http://localhost:3500

# Production (Docker)
docker compose build procurement-frontend
docker compose up -d procurement-frontend
# Access: http://localhost:8000/procurement/
```

---

## 📚 Documentation Links

- [React Router](https://reactrouter.com/)
- [TanStack Query](https://tanstack.com/query/latest)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Module Federation](https://module-federation.io/)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-07
**Status**: 🚧 Implementation Guide
**Estimated Completion**: 15-21 hours
