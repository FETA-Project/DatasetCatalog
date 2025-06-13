<template>
  <div>
    <div
      class="min-h-screen bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100 flex items-center justify-center"
    >
      <div
        class="w-full max-w-md text-center p-6 rounded-lg shadow-lg bg-gray-100 dark:bg-gray-800"
      >
        <h1 class="text-2xl font-bold mb-4">You've been logged out</h1>

        <p class="mb-4">You've successfully logged out of this service.</p>

        <p class="text-sm text-gray-600 dark:text-gray-400">
          You may still be logged in via your institutional login. To fully log
          out, close your browser.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
onMounted(() => {
  if (localStorage.getItem("darkMode") === "true") {
    document.documentElement.classList.add("dark");
  }
});
</script>
