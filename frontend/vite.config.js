import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import os from 'os'

function getLanIP() {
  for (const ifaces of Object.values(os.networkInterfaces())) {
    for (const iface of ifaces) {
      if (iface.family === 'IPv4' && !iface.internal) return iface.address
    }
  }
  return 'localhost'
}

const LAN_IP = getLanIP()

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    hmr: { host: LAN_IP, port: 5173, protocol: 'ws' },
    proxy: {
      '/feed':        { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/preferences': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
