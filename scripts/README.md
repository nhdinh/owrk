# Frontend Build Scripts

This directory contains scripts for building and deploying frontend services without rebuilding Docker images.

## Available Scripts

### 1. `build_fe.sh` - Full Build with Dependencies

**Use when:**
- First time setup
- After adding/updating npm packages
- After `package.json` changes
- When experiencing dependency-related errors

**What it does:**
1. Runs `npm install` for each service (ensures dependencies are up to date)
2. Builds production bundles with `npm run build`
3. Copies build output to running Docker containers

**Usage:**
```bash
# From project root
./scripts/build_fe.sh

# Or make executable first
chmod +x ./scripts/build_fe.sh
./scripts/build_fe.sh
```

**Time:** ~2-5 minutes (depending on npm install)

---

### 2. `build_fe_fast.sh` - Fast Build (Skip Dependencies)

**Use when:**
- Making code changes (not dependency changes)
- Iterative development
- Dependencies are already installed
- Quick rebuilds needed

**What it does:**
1. Skips `npm install` (assumes dependencies already present)
2. Builds production bundles with `npm run build`
3. Copies build output to running Docker containers

**Usage:**
```bash
# From project root
./scripts/build_fe_fast.sh

# Or make executable first
chmod +x ./scripts/build_fe_fast.sh
./scripts/build_fe_fast.sh
```

**Time:** ~30-60 seconds

---

## Services Built

Both scripts build and deploy all 4 frontend services:

1. **shared-components** → Container: `shared-components`
   - Module Federation host
   - Exposes shared components and AuthContext

2. **auth-frontend** → Container: `auth-fe`
   - Authentication and user management
   - Module Federation consumer

3. **asset-frontend** → Container: `asset-fe`
   - Asset management
   - Module Federation consumer

4. **dashboard-frontend** → Container: `dashboard-fe`
   - Main dashboard
   - Module Federation consumer

---

## Workflow

### Development Workflow

1. **First Time / After Dependency Changes:**
   ```bash
   ./scripts/build_fe.sh
   ```

2. **Iterative Development (Code Changes Only):**
   ```bash
   # Make your code changes
   ./scripts/build_fe_fast.sh
   # Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
   ```

3. **After Package.json Changes:**
   ```bash
   ./scripts/build_fe.sh
   ```

---

## How It Works

### Build Process

```
For each frontend service:
┌─────────────────────────────────────┐
│ 1. Navigate to service directory    │
├─────────────────────────────────────┤
│ 2. npm install (build_fe.sh only)   │
├─────────────────────────────────────┤
│ 3. npm run build                    │
│    - TypeScript compilation          │
│    - Vite production build           │
│    - Module Federation bundling      │
├─────────────────────────────────────┤
│ 4. Copy dist/ to Docker container   │
│    - Copy assets/                    │
│    - Copy index.html                 │
└─────────────────────────────────────┘
```

### Deployment

The scripts use `docker cp` to copy built files directly into running containers:

```bash
docker cp ./dist/assets <container>:/usr/share/nginx/html/
docker cp ./dist/index.html <container>:/usr/share/nginx/html/
```

**Benefits:**
- No need to rebuild Docker images
- No need to restart containers
- Changes take effect immediately after browser refresh
- Much faster than `docker compose build`

---

## Troubleshooting

### Error: "npm: command not found"

**Solution:** Install Node.js and npm on your system.

```bash
# Verify installation
node --version
npm --version
```

### Error: "docker cp: no such container"

**Solution:** Ensure Docker containers are running.

```bash
# Check container status
docker compose ps

# Start containers if not running
docker compose up -d
```

### Error: "Cannot find module '@originjs/vite-plugin-federation'"

**Solution:** Use `build_fe.sh` (with npm install) instead of `build_fe_fast.sh`.

```bash
./scripts/build_fe.sh
```

### Error: TypeScript compilation errors

**Solution:**
1. Check the error message
2. Fix the TypeScript errors in source code
3. Rebuild

### Changes not appearing in browser

**Solution:** Hard refresh the browser.

- **Windows/Linux:** `Ctrl + Shift + R` or `Ctrl + F5`
- **Mac:** `Cmd + Shift + R`
- **Or:** Open DevTools → Right-click refresh → "Empty Cache and Hard Reload"

---

## Performance Comparison

| Task | build_fe.sh | build_fe_fast.sh | docker compose build |
|------|-------------|------------------|---------------------|
| **Time** | ~2-5 min | ~30-60 sec | ~5-10 min |
| **Use Case** | First time / Dependencies changed | Code changes only | Dockerfile changes |
| **npm install** | ✅ Yes | ❌ No | ✅ Yes |
| **Container restart** | ❌ No | ❌ No | ✅ Yes |

---

## Tips

1. **Use `build_fe_fast.sh` for most development work** - It's much faster!

2. **Only use `build_fe.sh` when needed** - After adding packages or on first setup

3. **Always hard refresh** - After deploying changes, hard refresh your browser

4. **Check build output** - Look for TypeScript or build errors in the terminal

5. **Module Federation** - Changes to shared-components affect all consumer apps

6. **Parallel development** - You can run the script while containers are running

---

## Example Development Session

```bash
# Day 1 - First time setup
./scripts/build_fe.sh

# Make code changes to auth-frontend
vim services/auth-frontend/src/pages/Login.tsx

# Quick rebuild
./scripts/build_fe_fast.sh

# Test in browser (with hard refresh)

# Make more changes
vim services/auth-frontend/src/pages/Users.tsx

# Quick rebuild again
./scripts/build_fe_fast.sh

# Day 2 - Add new dependency
cd services/auth-frontend
npm install react-query

# Full rebuild (because package.json changed)
cd ../..
./scripts/build_fe.sh
```

---

## Module Federation Notes

When working with Module Federation:

1. **shared-components changes affect all apps** - If you modify shared-components, all consumer apps will use the new version after refresh

2. **Build order doesn't matter** - The scripts build in a specific order, but Module Federation loads at runtime

3. **remoteEntry.js** - Each build updates the Module Federation entry point

4. **Shared dependencies** - React and ReactDOM are shared singletons across all apps

---

## See Also

- [Module Federation Implementation](../docs/deliveries/MODULE_FEDERATION_IMPLEMENTATION.md)
- [CLAUDE.md](../CLAUDE.md) - Project overview and guidelines
- [Docker Compose](../docker-compose.yml) - Service configuration
