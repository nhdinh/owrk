import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import federation from "@originjs/vite-plugin-federation";
import path from "path";

export default defineConfig({
  base: "/shared/",
  plugins: [
    react(),
    federation({
      name: "shared_components",
      filename: "remoteEntry.js",
      exposes: {
        // Core components
        "./AuthContext": "./src/contexts/AuthContext.tsx",
        "./AppSidebar": "./src/components/AppSidebar.tsx",
        "./AppLayout": "./src/components/AppLayout.tsx",

        // Utilities
        "./utils": "./src/lib/utils.ts",

        // UI Components (expose with both kebab-case and PascalCase for compatibility)
        "./ui/accordion": "./src/components/ui/accordion.tsx",
        "./ui/alert-dialog": "./src/components/ui/alert-dialog.tsx",
        "./ui/alert": "./src/components/ui/alert.tsx",
        "./ui/aspect-ratio": "./src/components/ui/aspect-ratio.tsx",
        "./ui/avatar": "./src/components/ui/avatar.tsx",
        "./ui/badge": "./src/components/ui/badge.tsx",
        "./ui/breadcrumb": "./src/components/ui/breadcrumb.tsx",
        "./ui/button": "./src/components/ui/button.tsx",
        "./ui/calendar": "./src/components/ui/calendar.tsx",
        "./ui/card": "./src/components/ui/card.tsx",
        "./ui/carousel": "./src/components/ui/carousel.tsx",
        // "./ui/chart": "./src/components/ui/chart.tsx", // Has TypeScript errors with recharts types
        "./ui/checkbox": "./src/components/ui/checkbox.tsx",
        "./ui/collapsible": "./src/components/ui/collapsible.tsx",
        "./ui/command": "./src/components/ui/command.tsx",
        "./ui/context-menu": "./src/components/ui/context-menu.tsx",
        "./ui/dialog": "./src/components/ui/dialog.tsx",
        "./ui/drawer": "./src/components/ui/drawer.tsx",
        "./ui/dropdown-menu": "./src/components/ui/dropdown-menu.tsx",
        "./ui/form": "./src/components/ui/form.tsx",
        "./ui/hover-card": "./src/components/ui/hover-card.tsx",
        "./ui/input-otp": "./src/components/ui/input-otp.tsx",
        "./ui/input": "./src/components/ui/input.tsx",
        "./ui/label": "./src/components/ui/label.tsx",
        "./ui/menubar": "./src/components/ui/menubar.tsx",
        "./ui/navigation-menu": "./src/components/ui/navigation-menu.tsx",
        "./ui/pagination": "./src/components/ui/pagination.tsx",
        "./ui/popover": "./src/components/ui/popover.tsx",
        "./ui/progress": "./src/components/ui/progress.tsx",
        "./ui/radio-group": "./src/components/ui/radio-group.tsx",
        "./ui/resizable": "./src/components/ui/resizable.tsx",
        "./ui/scroll-area": "./src/components/ui/scroll-area.tsx",
        "./ui/select": "./src/components/ui/select.tsx",
        "./ui/separator": "./src/components/ui/separator.tsx",
        "./ui/sheet": "./src/components/ui/sheet.tsx",
        "./ui/sidebar": "./src/components/ui/sidebar.tsx",
        "./ui/skeleton": "./src/components/ui/skeleton.tsx",
        "./ui/slider": "./src/components/ui/slider.tsx",
        "./ui/sonner": "./src/components/ui/sonner.tsx",
        "./ui/switch": "./src/components/ui/switch.tsx",
        "./ui/table": "./src/components/ui/table.tsx",
        "./ui/tabs": "./src/components/ui/tabs.tsx",
        "./ui/textarea": "./src/components/ui/textarea.tsx",
        "./ui/toast": "./src/components/ui/toast.tsx",
        "./ui/toaster": "./src/components/ui/toaster.tsx",
        "./ui/toggle-group": "./src/components/ui/toggle-group.tsx",
        "./ui/toggle": "./src/components/ui/toggle.tsx",
        "./ui/tooltip": "./src/components/ui/tooltip.tsx",
      },
      shared: {
        react: {
          singleton: true,
          requiredVersion: "^18.3.1",
        },
        "react-dom": {
          singleton: true,
          requiredVersion: "^18.3.1",
        },
      },
    }),
  ],
  build: {
    modulePreload: false,
    target: "esnext",
    minify: false,
    cssCodeSplit: false,
  },
  server: {
    host: "0.0.0.0",
    port: 3400,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
