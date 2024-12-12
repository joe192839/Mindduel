/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "../../quiz/templates/**/*.html",     // Note the ../ to go up directories
      "../../theme/templates/**/*.html",
      "../../templates/quickplay/**/*.html",
      "../../templates/**/*.html"
    ],
    theme: {
      extend: {},
    },
    plugins: [
      require('@tailwindcss/forms'),
      require('@tailwindcss/typography'),
      require('@tailwindcss/aspect-ratio')
    ]
  }