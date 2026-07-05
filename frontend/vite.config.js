import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server runs on port 3000 (matching the original project) and proxies
// any /api call through to the Flask backend on port 3001, so the browser only
// ever talks to one origin during development.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: process.env.VITE_API_URL || "http://127.0.0.1:3001",
        changeOrigin: true,
      },
    },
  },
});
