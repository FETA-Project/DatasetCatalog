<template>
  <Toast position="bottom-right" />
  <MainMenu />
  <MDC class="m-4 max-w-[100%] prose dark:prose-invert" :value="howto_md" />
</template>

<script setup>
import axios from "axios";
import { useToast } from "primevue/usetoast";
import MainMenu from "@/components/menu.vue";

const toast = useToast();
const howto_md = ref(null);

onMounted(() => {
  axios
    .get("/api/howto")
    .then((response) => {
      console.log(response);
      howto_md.value = response.data;
    })
    .catch((error) => {
      howto_md.value = "Error while getting howto.md";
      console.log(error);
      toast.add({
        severity: "error",
        summary: "Error while howto.md",
        detail: error.response.data,
        life: 3000,
      });
    });
});
</script>
