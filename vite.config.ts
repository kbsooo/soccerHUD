import { defineConfig } from 'vite';
import chromeExtension from 'vite-plugin-chrome-extension';
import manifest from './src/manifest.json';

export default defineConfig({
  plugins: [chromeExtension({ manifest })],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: true
  }
});
