/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js,py}", "!./src/static/**/*"],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}

