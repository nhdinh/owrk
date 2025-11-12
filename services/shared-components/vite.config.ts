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

        // UI Components (expose entire files, consumers import what they need)
        "./Accordion": "./src/components/ui/accordion.tsx",
        "./AlertDialog": "./src/components/ui/alert-dialog.tsx",
        "./Alert": "./src/components/ui/alert.tsx",
        "./AspectRatio": "./src/components/ui/aspect-ratio.tsx",
        "./Avatar": "./src/components/ui/avatar.tsx",
        "./Badge": "./src/components/ui/badge.tsx",
        "./Breadcrumb": "./src/components/ui/breadcrumb.tsx",
        "./Button": "./src/components/ui/button.tsx",
        "./Calendar": "./src/components/ui/calendar.tsx",
        "./Card": "./src/components/ui/card.tsx",
        "./Carousel": "./src/components/ui/carousel.tsx",
        // "./Chart": "./src/components/ui/chart.tsx", // Has TypeScript errors with recharts types
        "./Checkbox": "./src/components/ui/checkbox.tsx",
        "./Collapsible": "./src/components/ui/collapsible.tsx",
        "./Command": "./src/components/ui/command.tsx",
        "./ContextMenu": "./src/components/ui/context-menu.tsx",
        "./Dialog": "./src/components/ui/dialog.tsx",
        "./Drawer": "./src/components/ui/drawer.tsx",
        "./DropdownMenu": "./src/components/ui/dropdown-menu.tsx",
        "./Form": "./src/components/ui/form.tsx",
        "./HoverCard": "./src/components/ui/hover-card.tsx",
        "./InputOtp": "./src/components/ui/input-otp.tsx",
        "./Input": "./src/components/ui/input.tsx",
        "./Label": "./src/components/ui/label.tsx",
        "./Menubar": "./src/components/ui/menubar.tsx",
        "./NavigationMenu": "./src/components/ui/navigation-menu.tsx",
        "./Pagination": "./src/components/ui/pagination.tsx",
        "./Popover": "./src/components/ui/popover.tsx",
        "./Progress": "./src/components/ui/progress.tsx",
        "./RadioGroup": "./src/components/ui/radio-group.tsx",
        "./Resizable": "./src/components/ui/resizable.tsx",
        "./ScrollArea": "./src/components/ui/scroll-area.tsx",
        "./Select": "./src/components/ui/select.tsx",
        "./Separator": "./src/components/ui/separator.tsx",
        "./Sheet": "./src/components/ui/sheet.tsx",
        "./Sidebar": "./src/components/ui/sidebar.tsx",
        "./Skeleton": "./src/components/ui/skeleton.tsx",
        "./Slider": "./src/components/ui/slider.tsx",
        "./Sonner": "./src/components/ui/sonner.tsx",
        "./Switch": "./src/components/ui/switch.tsx",
        "./Table": "./src/components/ui/table.tsx",
        "./Tabs": "./src/components/ui/tabs.tsx",
        "./Textarea": "./src/components/ui/textarea.tsx",
        "./Toast": "./src/components/ui/toast.tsx",
        "./Toaster": "./src/components/ui/toaster.tsx",
        "./ToggleGroup": "./src/components/ui/toggle-group.tsx",
        "./Toggle": "./src/components/ui/toggle.tsx",
        "./Tooltip": "./src/components/ui/tooltip.tsx",
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
