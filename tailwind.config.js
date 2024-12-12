/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./quiz/templates/**/*.html",     // For your quiz templates
    "./theme/templates/**/*.html",    // For your base template
    "./templates/quickplay/**/*.html", // For quickplay templates
    "./templates/**/*.html",          // For any other templates
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}