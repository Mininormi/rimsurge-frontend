/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      // 原来的 RAYS 域名
      {
        protocol: 'https',
        hostname: 'www.rayswheels.co.jp',
      },

      // 新增的 Freepik 加拿大国旗图标域名
      {
        protocol: 'https',
        hostname: 'cdn-icons-png.freepik.com',
      },
    ],
  },
  // Docker 环境下的文件监听配置
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // 启用轮询模式以支持 Docker 卷挂载的文件变化检测
      config.watchOptions = {
        poll: 1000, // 每秒轮询一次
        aggregateTimeout: 300, // 延迟 300ms 后重新构建
      }
    }
    return config
  },
}

export default nextConfig
