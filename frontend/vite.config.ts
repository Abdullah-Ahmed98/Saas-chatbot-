import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Inside Docker (dev via compose) the backend service is reachable by hostname;
// running locally without Docker it's on the host.
const isDocker = process.env.FRONTEND_IS_DOCKER === "1";
const backendTarget = isDocker ? "http://backend:8000" : "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      "/api": backendTarget,
    },
  },
});
