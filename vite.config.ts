import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const githubRepositoryName = process.env.GITHUB_REPOSITORY?.split('/').pop() ?? ''
const configuredRepositoryName = process.env.VITE_REPOSITORY_NAME ?? githubRepositoryName
const repositoryName = configuredRepositoryName.endsWith('.github.io') ? '' : configuredRepositoryName

export default defineConfig({
  plugins: [react()],
  base: repositoryName ? `/${repositoryName}/` : '/',
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'deck-gl': ['@deck.gl/core', '@deck.gl/layers', '@deck.gl/react'],
          charts: ['recharts'],
          react: ['react', 'react-dom'],
        },
      },
    },
  },
})
