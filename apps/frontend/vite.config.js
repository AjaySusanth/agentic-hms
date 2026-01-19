import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // Load env file from the current directory based on the 'mode' (development/production)
  // The third parameter '' allows loading all variables regardless of prefix
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    server: {
      host: true,      // Essential for Docker
      port: 3000,
      watch: {
        usePolling: true, // Essential for some Docker setups (Windows/WSL)
      },
      proxy: {
        '/api': {
          // Now 'env' is correctly defined here
          target: env.VITE_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});