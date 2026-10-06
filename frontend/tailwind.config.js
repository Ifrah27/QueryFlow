/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#EEF0FF',
          100: '#E0E4FF',
          500: '#5B5CE2',
          600: '#4F46E5',
          700: '#4338CA',
        },
        sidebar: {
          bg: '#0B1220',
          card: '#151D2A',
          hover: '#1E293B',
          text: '#94A3B8',
        },
      },
    },
  },
  plugins: [],
}
