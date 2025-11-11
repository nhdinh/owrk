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
        "./AuthContext": "./src/contexts/AuthContext.tsx",
        "./AppSidebar": "./src/components/AppSidebar.tsx",
        "./AppLayout": "./src/components/AppLayout.tsx",

        "./ui/Toaster": "./src/components/ui/sonner.tsx",
        "./ui/Tooltip": "./src/components/ui/tooltip.tsx",
        "./ui/TooltipTrigger": "./src/components/ui/tooltip.tsx",
        "./ui/TooltipContent": "./src/components/ui/tooltip.tsx",
        "./ui/TooltipProvider": "./src/components/ui/tooltip.tsx",
        "./ui/Button": "./src/components/ui/button.tsx",
        "./ui/Label": "./src/components/ui/label.tsx",
        "./ui/Input": "./src/components/ui/input.tsx",
        "./ui/AlertDialog": "./src/components/ui/alert-dialog.tsx",
        "./ui/AlertDialogPortal": "./src/components/ui/alert-dialog.tsx",
        "./ui/AlertDialogOverlay": "./src/components/ui/alert-dialog.tsx",
        "./ui/AlertDialogTrigger": "./src/components/ui/alert-dialog.tsx",
        "./ui/AlertDialogContent": "./src/components/ui/alert-dialog.tsx",
        "./ui/AlertDialogHeader": "./src/components/ui/alert-dialog.tsx",
        "./ui/AlertDialogFooter": "./src/components/ui/alert-dialog.tsx",
        "./ui/AlertDialogTitle": "./src/components/ui/alert-dialog.tsx",
        "./ui/AlertDialogDescription": "./src/components/ui/alert-dialog.tsx",
        "./ui/AlertDialogAction": "./src/components/ui/alert-dialog.tsx",
        "./ui/AlertDialogCancel": "./src/components/ui/alert-dialog.tsx",
        "./ui/Calendar": "./src/components/ui/calendar.tsx",

        "./ui/CarouselApi": "./src/components/ui/carousel.tsx",
        "./ui/Carousel": "./src/components/ui/carousel.tsx",
        "./ui/CarouselContent": "./src/components/ui/carousel.tsx",
        "./ui/CarouselItem": "./src/components/ui/carousel.tsx",
        "./ui/CarouselPrevious": "./src/components/ui/carousel.tsx",
        "./ui/CarouselNext": "./src/components/ui/carousel.tsx",

        "./ui/Pagination": "./src/components/ui/pagination.tsx",
        "./ui/PaginationContent": "./src/components/ui/pagination.tsx",
        "./ui/PaginationEllipsis": "./src/components/ui/pagination.tsx",
        "./ui/PaginationItem": "./src/components/ui/pagination.tsx",
        "./ui/PaginationLink": "./src/components/ui/pagination.tsx",
        "./ui/PaginationNext": "./src/components/ui/pagination.tsx",
        "./ui/PaginationPrevious": "./src/components/ui/pagination.tsx",

        "./ui/Separator": "./src/components/ui/separator.tsx",

        "./ui/Sheet": "./src/components/ui/sheet.tsx",
        "./ui/SheetClose": "./src/components/ui/sheet.tsx",
        "./ui/SheetContent": "./src/components/ui/sheet.tsx",
        "./ui/SheetDescription": "./src/components/ui/sheet.tsx",
        "./ui/SheetFooter": "./src/components/ui/sheet.tsx",
        "./ui/SheetHeader": "./src/components/ui/sheet.tsx",
        "./ui/SheetOverlay": "./src/components/ui/sheet.tsx",
        "./ui/SheetPortal": "./src/components/ui/sheet.tsx",
        "./ui/SheetTitle": "./src/components/ui/sheet.tsx",
        "./ui/SheetTrigger": "./src/components/ui/sheet.tsx",

        "./ui/Sidebar": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarContent": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarFooter": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarGroup": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarGroupAction": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarGroupContent": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarGroupLabel": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarHeader": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarInput": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarInset": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarMenu": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarMenuAction": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarMenuBadge": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarMenuButton": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarMenuItem": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarMenuSkeleton": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarMenuSub": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarMenuSubButton": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarMenuSubItem": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarProvider": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarRail": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarSeparator": "./src/components/ui/sidebar.tsx",
        "./ui/SidebarTrigger": "./src/components/ui/sidebar.tsx",
        "./ui/useSidebar": "./src/components/ui/sidebar.tsx",
        "./ui/Skeleton": "./src/components/ui/skeleton.tsx",

        "./ui/Badge": "./src/components/ui/badge.tsx",
        "./ui/badgeVariants": "./src/components/ui/badge.tsx",
        
        "./ui/Card": "./src/components/ui/card.tsx",
        "./ui/CardHeader": "./src/components/ui/card.tsx",
        "./ui/CardFooter": "./src/components/ui/card.tsx",
        "./ui/CardTitle": "./src/components/ui/card.tsx",
        "./ui/CardDescription": "./src/components/ui/card.tsx",
        "./ui/CardContent": "./src/components/ui/card.tsx",

        "./ui/Avatar": "./src/components/ui/avatar.tsx",
        "./ui/AvatarImage": "./src/components/ui/avatar.tsx",
        "./ui/AvatarFallback": "./src/components/ui/avatar.tsx",

        "./ui/Alert": "./src/components/ui/alert.tsx",
        "./ui/AlertTitle": "./src/components/ui/alert.tsx",
        "./ui/AlertDescription": "./src/components/ui/alert.tsx",

        "./ui/Tabs": "./src/components/ui/tabs.tsx",
        "./ui/TabsList": "./src/components/ui/tabs.tsx",
        "./ui/TabsTrigger": "./src/components/ui/tabs.tsx",
        "./ui/TabsContent": "./src/components/ui/tabs.tsx",


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
