/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Enable static exports
  images: {
    unoptimized: true,  // Required for static export
  },

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

  // rewrites는 static export에서는 작동하지 않으므로 제거
};

module.exports = nextConfig; 