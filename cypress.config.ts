import { defineConfig } from 'cypress';

console.log('CYPRESS_BASE_URL:', process.env.CYPRESS_BASE_URL);

export default defineConfig({
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL,
    supportFile: false,
  },
})