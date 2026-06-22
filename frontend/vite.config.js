import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // GitHub Pages 部署时可通过 BASE_PATH 环境变量指定子路径，如 /fridge-manager-demo/
  base: process.env.BASE_PATH || '/',
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    // 设置 chunk 大小警告阈值
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        // 手动分包：将第三方依赖拆分为独立 chunk
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'antd-vendor': ['antd', '@ant-design/icons'],
          'echarts-vendor': ['echarts', 'echarts-for-react'],
          'utils-vendor': ['axios', 'dayjs']
        }
      }
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.js',
    css: true
  }
});
