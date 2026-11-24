/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        praxia: {
          blue: '#0A66C2',
          navy: '#0052CC',
          bg: '#F3F6F8',
          white: '#FFFFFF',
          green: '#10B981',
          slate: '#475569',
          border: '#E2E8F0',
          dark: '#0F172A',
          danger: '#EF4444',
          warning: '#F59E0B'
        }
      }
    },
  },
  plugins: [],
}
