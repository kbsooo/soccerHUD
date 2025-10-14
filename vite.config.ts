import { resolve } from 'path';
import { defineConfig } from 'vite';

const rootDir = resolve(__dirname, 'src');

export default defineConfig({
  publicDir: 'public',
  build: {
    emptyOutDir: true,
    outDir: 'dist',
    rollupOptions: {
      input: {
        'content-script': resolve(rootDir, 'content-script/index.ts'),
        'page-script': resolve(rootDir, 'page-script/index.ts'),
        'options/index': resolve(rootDir, 'options/index.html')
      },
      output: {
        entryFileNames: (chunkInfo) => {
          const name = chunkInfo.name.replace(/\\/g, '/');
          if (name === 'content-script') {
            return 'content-script/index.js';
          }
          if (name === 'page-script') {
            return 'page-script/index.js';
          }
          if (name === 'options/index') {
            return 'options/index.js';
          }
          return 'assets/[name].js';
        },
        chunkFileNames: 'chunks/[name].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name === 'styles.css') {
            return 'options/styles.css';
          }
          return 'assets/[name][extname]';
        }
      }
    }
  },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.ts'],
    coverage: {
      provider: 'v8'
    }
  }
});
