import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  server: {

    proxy: {
      '/search': {
        target: 'http://localhost:8080', // 后端 Spring Boot 服务器的位置
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/search/, '') // 根据需要调整路径
      },
    },
  },
});
