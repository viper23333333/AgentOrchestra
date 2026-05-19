/** @type {import('next').NextConfig} */
const nextConfig = {
  // React 严格模式
  reactStrictMode: true,

  // API 代理配置 - 将 /api 请求代理到后端服务
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },

  // WebSocket 代理（开发环境）
  async headers() {
    return [
      {
        source: '/ws/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ];
  },

  // 环境变量暴露给客户端
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL,
  },

  // 图片优化配置
  images: {
    domains: [],
    formats: ['image/avif', 'image/webp'],
  },

  // 实验性功能
  experimental: {
    optimizePackageImports: ['lucide-react', 'framer-motion'],
  },
};

module.exports = nextConfig;
