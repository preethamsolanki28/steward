import type { NextConfig } from "next";

const isDev = process.env.NODE_ENV === "development";

// Production: static export to web/out, served by steward-api at / (D18).
// Dev (`pnpm dev` on the host): /api/* is rewritten to steward-api on 127.0.0.1:8787;
// its Host guard accepts localhost:3000 only when STEWARD_DEV=1.
const nextConfig: NextConfig = isDev
  ? {
      async rewrites() {
        return [{ source: "/api/:path*", destination: "http://127.0.0.1:8787/api/:path*" }];
      },
    }
  : { output: "export" };

export default nextConfig;
