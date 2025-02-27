/** @type {import('tailwindcss').Config} */
const primeui = require("tailwindcss-primeui");
const typography = require("@tailwindcss/typography")

module.exports = {
    darkMode: 'class',
    content: ["./components/**/*.{js,vue,ts}", "./layouts/**/*.vue", "./pages/**/*.vue", "./plugins/**/*.{js,ts}", "./nuxt.config.{js,ts}", "./app.vue", "./error.vue"],
    plugins: [primeui, typography],
};