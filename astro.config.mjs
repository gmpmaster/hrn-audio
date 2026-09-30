// @ts-check
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://audio.hrnmedianetworks.com',
  build: { format: 'directory' },
  server: { port: 4322 },
});
