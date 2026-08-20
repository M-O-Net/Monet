import tailwindcss from "@tailwindcss/vite";
import { tanstackRouter } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { resolve } from "node:path";

// The implementation sandbox is served from an opaque origin (see src/sandbox/frame.ts), which makes
// every asset it loads — its own bundled module script included — a cross-origin request. These
// are public static files with no credentials attached, so a blanket allow is safe, and without
// it the sandbox silently fails to boot. The same header has to be set wherever the built site
// is served: apps/web/nginx.conf for Docker, render.yaml for the deploy.
const corsHeaders = { "Access-Control-Allow-Origin": "*" };

export default defineConfig({
  // tanstackRouter must precede react() — it generates routeTree.gen.ts that react()
  // then needs to see.
  plugins: [tanstackRouter({ routesDirectory: "./src/routes" }), react(), tailwindcss()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(import.meta.dirname, "index.html"),
        sandbox: resolve(import.meta.dirname, "sandbox.html"),
      },
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    // Accessed through Docker's port-forward (host port != container port, e.g. 5273->5173),
    // so the incoming Host header's port never matches what Vite serves on internally —
    // permissive here is fine for a local dev container, not exposed beyond localhost.
    allowedHosts: true,
    headers: corsHeaders,
  },
  preview: { headers: corsHeaders },
});
