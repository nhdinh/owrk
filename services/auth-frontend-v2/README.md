# Auth Frontend v2 - React + shadcn/ui

Modern React-based authentication frontend for the Asset Management System.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **shadcn/ui** - UI components based on Radix UI
- **React Router** - Routing
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **Axios** - HTTP client
- **TanStack Query** - Data fetching & caching
- **Sonner** - Toast notifications

## Project Structure

```
src/
├── components/
│   └── ui/           # shadcn/ui components
├── lib/
│   ├── api.ts        # Axios instance
│   ├── auth-api.ts   # Auth API client
│   ├── user-api.ts   # User API client
│   ├── role-api.ts   # Role API client
│   ├── auth-context.tsx  # Auth context provider
│   └── utils.ts      # Utility functions
├── pages/
│   ├── Login.tsx     # Login page
│   ├── VerifyOTP.tsx # OTP verification
│   ├── ForgotPassword.tsx
│   ├── Dashboard.tsx # Main dashboard
│   ├── Users.tsx     # User list
│   ├── UserDetail.tsx
│   ├── Roles.tsx     # Role list
│   ├── RoleDetail.tsx
│   └── Profile.tsx   # User profile
├── types/
│   └── auth.ts       # TypeScript types
├── hooks/            # Custom hooks
├── App.tsx           # Main app component
├── main.tsx          # Entry point
└── index.css         # Global styles
```

## Development

### Prerequisites

- Node.js 20+
- npm or yarn

### Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

4. Open http://localhost:3100

### Build

```bash
npm run build
```

The build output will be in the `dist/` directory.

## Docker

### Build Docker image

```bash
docker build -t auth-frontend-v2 .
```

### Run container

```bash
docker run -p 3100:80 auth-frontend-v2
```

## Features

### Authentication
- ✅ Email/Password login
- ✅ 2FA/MFA with TOTP
- ✅ OTP verification
- ✅ Password reset
- ✅ Session management

### User Management
- ✅ User list with search & filters
- ✅ User detail view
- ✅ Create/Edit users
- ✅ Activate/Deactivate users
- ✅ Assign roles

### Role Management
- ✅ Role list
- ✅ Role detail view
- ✅ Create/Edit roles
- ✅ Manage permissions

### Profile
- ✅ View profile
- ✅ Change password
- ✅ Enable/Disable MFA

## API Integration

The frontend communicates with the auth-api service running on port 8088.

API endpoints are configured in:
- `src/lib/auth-api.ts` - Authentication
- `src/lib/user-api.ts` - User management
- `src/lib/role-api.ts` - Role management

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8088/api/v1` |

## Styling

The application uses TailwindCSS with a custom design system defined in `src/index.css`.

Color scheme:
- Primary: Blue (#4A90E2)
- Secondary: Gray
- Accent: Green
- Destructive: Red

All colors use HSL format for better theme support.

## Components

This project uses shadcn/ui components, which are:
- Accessible (built on Radix UI)
- Customizable
- Copy-paste friendly
- Styled with TailwindCSS

To add new components:
```bash
npx shadcn-ui@latest add [component-name]
```

## Contributing

1. Follow the existing code style
2. Use TypeScript for type safety
3. Add proper error handling
4. Test all features before committing

## License

Internal use only - Asset Management System
