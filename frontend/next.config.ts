import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  
  // 🔥 기가차드 Hot Reload 지옥 방지!
  webpack: (config, { dev }) => {
    if (dev) {
      // 파일 변경 감지 최적화
      config.watchOptions = {
        ...config.watchOptions,
        poll: 1000, // 1초마다 폴링
        aggregateTimeout: 300, // 300ms 지연
        ignored: /node_modules/, // node_modules 무시
      };
    }
    return config;
  },
  
  rewrites: async () => {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8080/api/:path*",
      },
      {
        source: "/docs",
        destination:
          process.env.NODE_ENV === "development"
            ? "http://127.0.0.1:8000/api/docs"
            : "/api/docs",
      },
      {
        source: "/openapi.json",
        destination:
          process.env.NODE_ENV === "development"
            ? "http://127.0.0.1:8000/api/openapi.json"
            : "/api/openapi.json",
      },
    ];
  },
};

export default nextConfig;