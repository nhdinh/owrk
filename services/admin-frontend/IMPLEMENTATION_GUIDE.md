# Admin Frontend Implementation Guide

## Overview
Complete React 18 + Vite 5 + TypeScript frontend for Admin Management Service.

**Port**: 3500
**Route**: http://localhost:8000/admin/
**Pattern**: Module Federation consumer of shared-components

## Project Structure

```
admin-frontend/
├── public/
│   └── vite.svg
├── src/
│   ├── components/
│   │   ├── ui/               # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── form.tsx
│   │   │   ├── input.tsx
│   │   │   ├── label.tsx
│   │   │   ├── select.tsx
│   │   │   ├── switch.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── toast.tsx
│   │   │   └── alert-dialog.tsx
│   │   ├── layout/
│   │   │   └── AdminLayout.tsx
│   │   ├── trash/
│   │   │   ├── TrashList.tsx
│   │   │   ├── TrashItem.tsx
│   │   │   ├── TrashStats.tsx
│   │   │   ├── TrashFilters.tsx
│   │   │   ├── RestoreDialog.tsx
│   │   │   └── PermanentDeleteDialog.tsx
│   │   ├── settings/
│   │   │   ├── ModuleSettingsList.tsx
│   │   │   ├── SettingEdit Dialog.tsx
│   │   │   └── SettingForm.tsx
│   │   └── modules/
│   │       ├── SystemModulesList.tsx
│   │       └── ModuleCard.tsx
│   ├── lib/
│   │   ├── api.ts           # Axios instance
│   │   ├── auth-context.tsx  # Auth context
│   │   └── utils.ts          # Utility functions
│   ├── pages/
│   │   ├── Dashboard.tsx     # Admin dashboard
│   │   ├── TrashPage.tsx     # Trash management
│   │   ├── SettingsPage.tsx  # Module settings
│   │   ├── ModulesPage.tsx   # System modules
│   │   └── AuditLogsPage.tsx # Audit logs
│   ├── types/
│   │   ├── trash.ts
│   │   ├── settings.ts
│   │   └── modules.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── Dockerfile
├── nginx.conf
├── .dockerignore
├── .gitignore
├── components.json
├── eslint.config.js
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
└── vite.config.ts (✅ created)
```

## Configuration Files

### 1. tsconfig.json
```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ],
  "compilerOptions": {
    "composite": true,
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",

    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
```

### 2. tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

### 3. postcss.config.js
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### 4. components.json
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

### 5. index.html
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Admin - Office Equipment Management</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

## Core Implementation Files

### src/index.css
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

### src/lib/utils.ts
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatRelativeTime(date: string | Date): string {
  const now = new Date()
  const past = new Date(date)
  const diffMs = now.getTime() - past.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`
  return `${Math.floor(diffDays / 365)} years ago`
}
```

### src/lib/api.ts
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
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
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

// Admin API endpoints
export const adminAPI = {
  // Trash Management
  trash: {
    list: (params?: any) => api.get('/admin/trash/', { params }),
    stats: () => api.get('/admin/trash/stats'),
    get: (id: number) => api.get(`/admin/trash/${id}`),
    create: (data: any) => api.post('/admin/trash/', data),
    restore: (id: number, data: any) => api.post(`/admin/trash/${id}/restore`, data),
    permanentDelete: (id: number, data: any) => api.delete(`/admin/trash/${id}`, { data }),
  },

  // Trash Config
  trashConfig: {
    list: (params?: any) => api.get('/admin/trash/config/', { params }),
    get: (module: string, resource: string) =>
      api.get(`/admin/trash/config/${module}/${resource}`),
    create: (data: any) => api.post('/admin/trash/config/', data),
    update: (id: number, data: any) => api.put(`/admin/trash/config/${id}`, data),
    delete: (id: number) => api.delete(`/admin/trash/config/${id}`),
  },

  // Module Settings
  settings: {
    list: (params?: any) => api.get('/admin/module-settings/', { params }),
    getByModule: (module: string) => api.get(`/admin/module-settings/module/${module}`),
    get: (id: number) => api.get(`/admin/module-settings/${id}`),
    create: (data: any) => api.post('/admin/module-settings/', data),
    update: (id: number, data: any) => api.put(`/admin/module-settings/${id}`, data),
    delete: (id: number) => api.delete(`/admin/module-settings/${id}`),
    publicSettings: () => api.get('/admin/module-settings/public/'),
  },

  // System Modules
  modules: {
    list: () => api.get('/admin/system-modules/'),
    get: (id: number) => api.get(`/admin/system-modules/${id}`),
  },
};
```

### src/types/trash.ts
```typescript
export interface TrashItem {
  id: number;
  module_name: string;
  resource_type: string;
  resource_id: string;
  resource_name: string;
  resource_data: Record<string, any>;
  deleted_by: number;
  deleted_by_email?: string;
  deleted_at: string;
  deleted_reason?: string;
  is_restorable: boolean;
  permanent_delete_at?: string;
  restore_dependencies?: any[];
  extra_metadata?: Record<string, any>;
  restored_at?: string;
  restored_by?: number;
  restored_by_email?: string;
}

export interface TrashStats {
  total_items: number;
  total_size_kb?: number;
  by_module: Record<string, number>;
  by_type: Record<string, number>;
  restorable_count: number;
  scheduled_for_deletion: number;
  oldest_item?: string;
  newest_item?: string;
}

export interface TrashConfig {
  id: number;
  module_name: string;
  resource_type: string;
  auto_delete_days: number;
  enable_soft_delete: boolean;
  enable_restore: boolean;
  require_approval: boolean;
  cascade_delete: boolean;
  created_at: string;
  updated_at: string;
}
```

## Key Pages Implementation

### src/pages/TrashPage.tsx (Complete Example)

See separate TRASH_PAGE_EXAMPLE.md for complete implementation

### Dockerfile
```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

## Docker Compose Integration

Add to `docker-compose.yml`:

```yaml
  admin-frontend:
    build:
      context: ./services/admin-frontend
      dockerfile: Dockerfile
    container_name: admin-frontend
    ports:
      - 3500:80
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    depends_on:
      - admin-api
    networks:
      - officework_network
```

## Nginx API Gateway Update

Add to `nginx/nginx.conf`:

```nginx
# Admin Frontend
location ~ ^/admin(/.*)?$ {
    proxy_pass http://admin-frontend$1;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}
```

## shadcn/ui Component Installation

```bash
cd services/admin-frontend

# Install shadcn/ui components
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add form
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add select
npx shadcn@latest add switch
npx shadcn@latest add table
npx shadcn@latest add tabs
npx shadcn@latest add toast
npx shadcn@latest add alert-dialog
npx shadcn@latest add badge
npx shadcn@latest add separator
```

## Development Workflow

1. **Install dependencies**:
```bash
cd services/admin-frontend
npm install
```

2. **Run dev server**:
```bash
npm run dev
# Access at http://localhost:3500
```

3. **Build for production**:
```bash
npm run build
```

4. **Docker build**:
```bash
docker compose build admin-frontend
docker compose up -d admin-frontend
# Access at http://localhost:8000/admin/
```

## Feature Checklist

- [✅] Project structure created
- [✅] Configuration files (vite, tailwind, typescript)
- [✅] API client setup
- [✅] Type definitions
- [ ] Auth context integration
- [ ] Layout with Module Federation sidebar
- [ ] Trash Management UI (list, filter, restore, delete)
- [ ] Module Settings UI (CRUD operations)
- [ ] System Modules UI (view, status)
- [ ] Audit Logs UI (view, filter)
- [ ] Dashboard with statistics
- [ ] Docker integration
- [ ] Nginx routing

## Next Steps

1. Copy UI components from auth-frontend or use shadcn/ui CLI
2. Implement TrashPage.tsx following the example
3. Implement SettingsPage.tsx for module settings
4. Implement ModulesPage.tsx for system modules
5. Create AdminLayout with Module Federation integration
6. Test with admin-api backend
7. Deploy with Docker

## Reference

- Auth Frontend: `services/auth-frontend/`
- Shared Components: `services/shared-components/`
- Admin API Docs: http://localhost:8005/docs
- Module Federation Guide: docs/deliveries/MODULE_FEDERATION_IMPLEMENTATION.md
