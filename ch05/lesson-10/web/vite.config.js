import { defineConfig } from "vite";

export default defineConfig({
  // #region dev-proxy
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    proxy: {
      "^/questions(?:/|\\?|$)": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  // #endregion dev-proxy
  // #region preview
  preview: {
    host: "127.0.0.1",
    port: 4173,
    strictPort: true,
    proxy: {},
  },
  // #endregion preview
});
