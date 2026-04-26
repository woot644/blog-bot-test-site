/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#0A0A0F',
          900: '#13131A',
          800: '#1F1F2A',
          700: '#2A2A3A',
        },
        accent: {
          400: '#7DD3FC',
          500: '#38BDF8',
          600: '#0EA5E9',
        },
      },
      fontFamily: {
        heading: ['Inter', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
