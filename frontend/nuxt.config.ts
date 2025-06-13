import Lara from '@primevue/themes/lara';

export default defineNuxtConfig({
app:{
    head: {
      title: "Katoda - Dataset Catalog",
      link: [
          {
              rel: 'icon',
              type: 'image/svg+xml',
              href: '/favicon.svg'
          }
      ]
    },
},
  ssr: true,
  modules: [
      '@nuxtjs/tailwindcss',
      '@primevue/nuxt-module',
      '@nuxtjs/google-fonts',
      '@nuxtjs/mdc',
  ],

  css: [
      'primeicons/primeicons.css',
    //   '@/assets/styles/base.css',
    //   '@/assets/styles/tailwind.css'
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
                  darkModeSelector: '.dark',
               },
          },
      }
  },

  postcss: {
      plugins: {
          'postcss-import': {},
          tailwindcss: {},
          autoprefixer: {}
      }
  },

  compatibilityDate: '2025-02-24',
})