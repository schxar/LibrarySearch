import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  server: {

    host: '0.0.0.0', // 或者使用你的内网IP地址 port: 5173,


  },
});
