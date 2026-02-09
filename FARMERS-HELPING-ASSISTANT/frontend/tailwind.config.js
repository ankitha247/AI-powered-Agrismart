/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9f0',
          100: '#dcf2dc',
          500: '#2e7d32',
          600: '#1b5e20',
          700: '#0d4d0d',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}