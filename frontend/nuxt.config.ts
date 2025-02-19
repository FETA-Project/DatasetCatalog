import Lara from '@primevue/themes/lara';

export default defineNuxtConfig({
    // ssr: false,
    modules: [
        '@primevue/nuxt-module',
        '@nuxtjs/google-fonts',
        '@nuxtjs/tailwindcss'
    ],
    css: [
        'primeicons/primeicons.css',
        // '@/assets/styles/base.css',
        // '@/assets/styles/tailwind.css'
    ],
    googleFonts: {
      families: {
        // "DM Sans": true,
        "Inter": true,
        // "Noto Serif": true,
        // Roboto: [100, 400],
      }
    },
    primevue: {
        options: {
            ripple: false,
            // inputVariant: 'outlined',
            theme: {
                preset: Lara,
                 options: {
                    darkModeSelector: '.dark-mode',
                }
            }
        }
    },
    postcss: {
        plugins: {
            'postcss-import': {},
            tailwindcss: {},
            autoprefixer: {}
        }
    }
})
