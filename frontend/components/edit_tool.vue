<template>
  <div id="container" class="card flex justify-center">
    <div class="flex flex-col gap-4 container">
      <Toast position="bottom-right" />
      <div id="name" class="flex flex-col gap-2">
        <label for="title">
            <i class="pi pi-info-circle" v-tooltip.right="'Short name of the collection tool (e.g. ipfixprobe) which is used as the unique identifier'" />
            Collection Tool Name
        </label>
        <InputText
          id="name"
          v-model="name"
          aria-describedby="acronym-help"
          placeholder="Collection Tool Name"
          readonly
        />
      </div>
      <div id="url" class="flex flex-col gap-2">
        <label for="url">
            <i class="pi pi-info-circle" v-tooltip.right="'URL where the collection tool may be found.'" />
            URL
        </label>
           <InputText
            id="url"
            v-model="url"
            aria-describedby="url-help"
            placeholder="URL"
            /> 
        </div>
      <div id="description" class="flex flex-col gap-2">
        <label for="Description">
            <i class="pi pi-info-circle" v-tooltip.right="'Overview description of the collection tool'" />
            Description
        </label>
        <TextArea
          id="description"
          v-model="description"
          aria-describedby="description-help"
          placeholder="Description..."
          rows="5"
          cols="30"
          v-tooltip.bottom="'The description of the dataset.'"
        />
      </div>
      <div id="known_issues" class="flex flex-col gap-2">
        <label for="Known Issues">
            <i class="pi pi-info-circle" v-tooltip.right="'Known issues of the collection tool'" />
            Known Issues
        </label>
        <TextArea
          id="known_issues"
          v-model="known_issues"
          aria-describedby="known_issues-help"
          placeholder="Known Issues..."
          rows="5"
          cols="30"
          v-tooltip.bottom="'The known issues of the dataset.'"
        />
      </div>
        <Button
          label="Edit Tool"
          icon="pi pi-upload"
          @click="makeRequest"
          class="w-4/12"
        />
      <footer><small>* required field</small></footer>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import axios from "axios";


const router = useRouter();

const toast = useToast();

const dialogRef = inject("dialogRef")

const name = ref("");
const description = ref("");
const descriptionError = ref(false);
const known_issues = ref("");
const known_issuesError = ref(false);
const url = ref("");
const urlError = ref(false);

onMounted(() => {
    name.value = dialogRef.value.data.name;
    description.value = dialogRef.value.data.description;
    known_issues.value = dialogRef.value.data.known_issues;
    url.value = dialogRef.value.data.url;
})

async function makeRequest(event) {
  const formData = new FormData();
  formData.append("description", description.value);
  formData.append("known_issues", known_issues.value);
  formData.append("url", url.value);

  formData.forEach(element => {
    console.log(element)
  });

  await axios
    .post(`/api/collectionTools/${encodeURIComponent(name.value)}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data', // Make sure to set the correct content type
      },
    })
    .then((response) => {
      console.log(response.data);
      dialogRef.value.close(name.value)
    })
    .catch((error) => {
      console.log(error)
      toast.add({
        severity: "error",
        summary: "Edit Error",
        detail: error.response.data.detail,
        life: 3000,
      });
    });
}

</script>

<style scoped>

.container {
    width: 30em;
}
.error {
  color: red;
}

.error > * {
  border-color: red;
}

label {
  font-weight: bold;
}
</style>
