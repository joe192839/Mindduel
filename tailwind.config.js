/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./quiz/templates/**/*.html",     // For your quiz templates
    "./theme/templates/**/*.html",    // For your base template
    "./templates/quickplay/**/*.html", // For quickplay templates
    "./templates/**/*.html",          // For any other templates
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#F0FBFF',
          100: '#E6F6FF',
          200: '#B3E3FF',
          300: '#80D0FF',
          400: '#4DBDFF',
          500: '#009fdc',
          600: '#0080B3',
          700: '#006080',
        },
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(180deg, var(--primary-500) 0%, var(--primary-200) 100%)',
      },
    },
  },
  plugins: [],
}