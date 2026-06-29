/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        wordle: {
          green: '#86a373',
          yellow: '#c6b66d',
          gray: '#7b7b7c',
          bg: '#f0f2f5',
          darkBg: '#1a1a2e',
        },
      },
    },
  },
  plugins: [],
}
