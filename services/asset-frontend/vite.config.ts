import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import federation from "@originjs/vite-plugin-federation";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  base: "/assets/",
  plugins: [
    react(),
    federation({
      name: 'asset_app',
      remotes: {
        shared_components: 'http://localhost:8000/shared/assets/remoteEntry.js',
      },
      shared: {
        react: {
          singleton: true,
          requiredVersion: '^18.3.1',
        },
        'react-dom': {
          singleton: true,
          requiredVersion: '^18.3.1',
        },
      },
    }),
  ],
  build: {
    modulePreload: false,
    target: 'esnext',
    minify: false,
    terserOptions: {
      compress: false, // Prevents code compression
      mangle: false,   // Prevents variable and function name mangling
      format: {
        comments: true, // Retains comments (optional, adjust as needed)
      },
    },
    cssCodeSplit: false,
  },
  server: {
    host: "0.0.0.0",
    port: 3200,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
