# Procurement Frontend

Modern procurement management frontend built with React, TypeScript, and Vite.

## Features

- 🛒 Purchase Request Management
- 🏢 Vendor Management
- 💰 Quotation Management & Comparison
- 📦 Purchase Order Tracking
- 🔐 Authentication & Authorization
- 📱 Responsive Design
- 🎨 Modern UI with shadcn/ui

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite 5
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: TanStack Query
- **Routing**: React Router v6
- **Module Federation**: @originjs/vite-plugin-federation

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn

### Installation

```bash
cd services/procurement-frontend
npm install
```

### Development

```bash
npm run dev
# Access at http://localhost:3500
```

### Build

```bash
npm run build
```

### Docker

```bash
# Build
docker build -t procurement-frontend .

# Run
docker run -p 3500:80 procurement-frontend
```

## Project Structure

```
src/
├── components/       # Reusable components
│   ├── ui/          # shadcn/ui components
│   ├── purchase-requests/
│   ├── vendors/
│   ├── quotations/
│   └── purchase-orders/
├── pages/           # Page components
├── lib/             # Utilities, API client, contexts
├── hooks/           # Custom React hooks
├── types/           # TypeScript type definitions
├── App.tsx          # Main app component
└── main.tsx         # Entry point
```

## Environment Variables

Create a `.env` file:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Integration

### API Gateway
- Base URL: http://localhost:8000/procurement/
- API: http://localhost:8000/api/v1

### Shared Components
Uses Module Federation to load shared components from:
- http://localhost:8000/shared/assets/remoteEntry.js

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Contributing

See [PROCUREMENT_FRONTEND_IMPLEMENTATION_GUIDE.md](../../docs/deliveries/PROCUREMENT_FRONTEND_IMPLEMENTATION_GUIDE.md) for detailed implementation guide.

## License

Proprietary - Office Equipment Management System
