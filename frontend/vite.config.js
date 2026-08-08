import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Proxy API requests to backend during development
      '/api': 'http://localhost:8000',
      '/candidates.json': 'http://localhost:8000',
      '/curriculum.json': 'http://localhost:8000'
    }
  }
})
