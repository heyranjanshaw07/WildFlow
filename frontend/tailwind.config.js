/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#0f172a',
          800: '#1e293b',
          700: '#334155',
          600: '#475569',
          500: '#64748b',
        },
        wind: {
          primary: '#1e40af', // Deep enterprise blue
          accent: '#0d9488',  // Restrained teal/green
          light: '#f0fdf4',
          alert: '#dc2626',
          warning: '#d97706',
        }
      }
    },
  },
  plugins: [],
}
