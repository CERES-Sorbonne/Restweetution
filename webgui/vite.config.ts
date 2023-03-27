import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/collector_api': {
           target: 'http://localhost:3300',
           changeOrigin: true,
           secure: false,      
           ws: true,
           rewrite: (path) => path.replace(/^\/collector_api/, '')
       },
       '/storage_api': {
        target: 'http://localhost:3301',
        changeOrigin: true,
        secure: false,      
        ws: true,
        rewrite: (path) => path.replace(/^\/storage_api/, '')
    }
    }
  }
});
