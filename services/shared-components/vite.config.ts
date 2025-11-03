import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import federation from '@originjs/vite-plugin-federation';
import path from 'path';

export default defineConfig({
  base: '/shared/',
  plugins: [
    react(),
    federation({
      name: 'shared_components',
      filename: 'remoteEntry.js',
      exposes: {
        './AppSidebar': './src/components/AppSidebar.tsx',
        './AppLayout': './src/components/AppLayout.tsx',
        './AuthContext': './src/contexts/AuthContext.tsx',
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
    cssCodeSplit: false,
  },
  server: {
    host: '0.0.0.0',
    port: 3400,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
