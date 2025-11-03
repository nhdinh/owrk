# Asset Frontend V2 - Implementation Guide

## Current Status

### ✅ Completed
1. **Project initialized** with Vite + React + TypeScript
2. **Dependencies installed** (373 packages)
3. **Configuration files copied** from auth-frontend:
   - tailwind.config.ts
   - postcss.config.js
   - tsconfig.json
   - vite.config.ts
4. **UI Components copied** from auth-frontend (src/components/ui/)
5. **Lib utilities copied** (src/lib/utils.ts)
6. **Types created**:
   - src/types/asset.ts ✅
   - src/types/auth.ts ✅
7. **API clients created**:
   - src/lib/api.ts ✅
   - src/lib/asset-api.ts ✅
   - src/lib/auth-context.tsx ✅

### 🚧 Remaining Tasks

You need to create the following page files. The complete code for each was provided by the agent earlier in the conversation.

#### 1. src/pages/Assets.tsx
Main assets list page with table, filters, search, and pagination.

#### 2. src/pages/AssetDetail.tsx
Asset detail page with tabs for assignment and maintenance history.

#### 3. src/pages/AssetForm.tsx
Create/edit asset form with validation using react-hook-form + zod.

#### 4. src/App.tsx
Main app component with routing and authentication.

#### 5. src/main.tsx
Entry point.

####6. src/index.css
Tailwind CSS setup.

#### 7. index.html
HTML template.

#### 8. Add Textarea component
Copy from auth-frontend or create:
```bash
cp services/auth-frontend/src/components/ui/textarea.tsx services/asset-frontend/src/components/ui/
```

## Docker Configuration

### Dockerfile
```dockerfile
FROM node:18-alpine AS builder
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

    # Proxy API requests to asset-api
    location /api/ {
        proxy_pass http://asset-api:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### .dockerignore
```
node_modules
dist
.git
.env.local
```

### .env.example
```
VITE_ASSET_API_BASE_URL=http://localhost:8002/api/v1
VITE_AUTH_API_BASE_URL=http://localhost:8001/api/v1
```

## Add to docker-compose.yml

```yaml
  asset-fe:
    build:
      context: ./services/asset-frontend
      dockerfile: Dockerfile
    container_name: asset-fe
    ports:
      - "3200:80"
    environment:
      - NODE_ENV=production
    depends_on:
      - asset-api
      - auth-api
    networks:
      - officework_network
    restart: unless-stopped
```

## Building and Running

### Development
```bash
cd services/asset-frontend
npm run dev
# Access at http://localhost:5173
```

### Production
```bash
cd services/asset-frontend
npm run build
docker compose up -d asset-fe
# Access at http://localhost:3200
```

## Integration Points

1. **Authentication**: Shares localStorage tokens with auth-frontend
2. **API Base URL**: http://localhost:8002/api/v1 (asset-api)
3. **Auth Redirect**: Redirects to http://localhost:3100/login if not authenticated

## Quick Command to Create Remaining Files

The easiest way is to:
1. Ask Claude to provide each page file contents one by one
2. Copy-paste into the respective files
3. Or use the agent's response from earlier in this conversation

All the code was already generated - it just needs to be saved to files.
