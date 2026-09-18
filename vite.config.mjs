// 仅开发服务器代理；生产静态站点仍需 nginx 等反向代理。
// 目标地址从启动命令的环境变量读取，不进入浏览器构建产物。
export default {
  server: {
    proxy: {
      ...(process.env.CLASSROOM_API_PROXY ? {
        '/classroom-api/': { target: process.env.CLASSROOM_API_PROXY, changeOrigin: false },
      } : {}),
      ...(process.env.CLASSROOM_STUDENT_PROXY ? {
        '/classroom/': { target: process.env.CLASSROOM_STUDENT_PROXY, changeOrigin: false, ws: true },
      } : {}),
    },
  },
}
