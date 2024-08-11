<template>
  <div id="container" class="card flex justify-content-center">
    <div class="flex flex-column gap-3 container">
      <Toast position="bottom-right" />
      <div id="acronym" :class="{ error: acronymError }" class="flex flex-column gap-2">
        <label for="title">
            <i class="pi pi-info-circle" v-tooltip.right="'Acronym of the dataset'" />
            Dataset Acronym*
        </label>
        <InputText
          id="acronym"
          v-model="acronym"
          aria-describedby="acronym-help"
          placeholder="Dataset Acronym"
          @blur="acronymError = acronym.length === 0"
        />
        <small v-if="acronymError" class="p-error">
          <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
          Dataset Acronym is required and must be unique.
        </small>
      </div>
      <div id="title" :class="{ error: titleError }" class="flex flex-column gap-2">
        <label for="title">
            <i class="pi pi-info-circle" v-tooltip.right="'Title of the dataset'" />
            Dataset Title
        </label>
        <InputText
          id="title"
          v-model="title"
          aria-describedby="title-help"
          placeholder="Dataset Title"
        />
        <small v-if="titleError" class="p-error">
          <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
          Dataset Title is required.
        </small>
      </div>
      <div id="name" :class="{ error: nameError }" class="flex flex-column gap-2">
        <label for="name">
            <i class="pi pi-info-circle" v-tooltip.right="'Name and surname of the submitter.'" />
            Submitter Name
        </label>
        <InputText
          id="name"
          v-model="name"
          aria-describedby="name-help"
          placeholder="Name Surname"
        />
        <small v-if="nameError" class="p-error">
          <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
          Submitter Name is required.
        </small>
      </div>
      <div id="email" :class="{ error: emailError }" class="flex flex-column gap-2">
        <label for="email">
            <i class="pi pi-info-circle" v-tooltip.right="'Email of the submitter.'" />
            Submitter Email
        </label>
        <InputText
          id="email"
          v-model="email"
          aria-describedby="email-help"
          placeholder="submitter@email"
          />
        <small v-if="emailError" class="p-error">
          <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
          Submitter Email is required.
        </small>
      </div>
      <div id="paperTitle" :class="{ error: paperTitleError }" class="flex flex-column gap-2">
        <label for="paperTitle">
            <i class="pi pi-info-circle" v-tooltip.right="'Title of the dataset'" />
            Paper Title
        </label>
        <InputText
          id="paperTitle"
          v-model="paperTitle"
          aria-describedby="paperTitle-help"
          placeholder="Paper Title"
        />
        <small v-if="paperTitleError" class="p-error">
          <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
          Paper Title is required.
        </small>
      </div>
      <div id="paperTitle" :class="{ error: authorError }" class="flex flex-column gap-2">
        <label for="author">
            <i class="pi pi-info-circle" v-tooltip.right="'Title of the dataset'" />
            Dataset Author
        </label>
        <InputText
          id="author"
          v-model="author"
          aria-describedby="author-help"
          placeholder="Dataset Author"
        />
        <small v-if="authorError" class="p-error">
          <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
          Dataset Author is required.
        </small>
      </div>
      <div id="description" class="flex flex-column gap-2">
        <label for="Description">
            <i class="pi pi-info-circle" v-tooltip.right="'Description of the dataset.'" />
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
      <div id="tags" class="flex flex-column gap-2">
        <label for="tags">
            <i class="pi pi-info-circle" v-tooltip.right="'Tags (words split by comma) to describe the dataset.'" />
            Tags
        </label>
        <div class="card p-fluid p-hidden-label">
            <Chips 
              id="tags"
              v-model="tags"
              separator=","
              placeholder="Tag"
              add-on-blur="true"
              allow-duplicate="false"
              v-tooltip.bottom="'Tags to describe the dataset.'"
            />
        </div>
      </div>
      <div id="doi" class="flex flex-column gap-2">
        <label for="doi">
            <i class="pi pi-info-circle" v-tooltip.right="'DOI of the dataset.'" />
            DOI
        </label>
        <InputText
                id="doi"
                v-model="doi"
                :class="{ error: doiError }"
                aria-describedby="doi-help"
                placeholder="DOI"
                /> 
      </div>
      <div id="originsDoi" class="flex flex-column gap-2">
        <label for="originsDoi">
            <i class="pi pi-info-circle" v-tooltip.right="'Origins DOI of the dataset.'" />
            Origins DOI
        </label>
        <InputText
                id="originsDoi"
                v-model="originsDoi"
                :class="{ error: originsDoiError }"
                aria-describedby="originsDoi-help"
                placeholder="Origins DOI"
                /> 
      </div>
      <TabView id="dataset-upload">
        <TabPanel header="Local File">
          <FileUpload
            name="upload"
            :auto="false"
            :multiple="false"
            :fileLimit="1"
            custom-upload
            ref="fileUpload"
            @uploader="makeRequest"
            upload-label="Submit"
          >
            <template #empty>
              <p class="flex justify-content-center">
                Drag and drop file here to upload.
              </p>
            </template>
          </FileUpload>
        </TabPanel>
        <!-- <TabPanel header="URL">
            <div class="flex justify-content-center gap-2">
               <InputText
                id="url"
                v-model="url"
                :class="{ error: urlError }"
                aria-describedby="url-help"
                placeholder="URL"
                @blur="urlError = url.length === 0"
                class="w-8"
                /> 
                <Button
                  label="Submit"
                  icon="pi pi-upload"
                  @click="makeRequest"
                  class="w-4"
                />
            </div>
        </TabPanel> -->
      </TabView>
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

const acronym = ref("");
const acronymError = ref(false);
const title = ref("");
const titleError = ref(false);
const paperTitle = ref("");
const paperTitleError = ref(false);
const author = ref("");
const authorError = ref(false);
const description = ref("");
const descriptionError = ref(false);
const doi = ref("");
const doiError = ref(false);
const originsDoi = ref("");
const originsDoiError = ref(false);
const name = ref("");
const nameError = ref(false);
// TODO: check if email is valid
const email = ref("");
const emailError = ref(false);
const url = ref("");
const urlError = ref(false);
const fileUpload = ref(null);
const tags = ref();

function clearUpload() {
  fileUpload.value.clear()
  fileUpload.value.uploadedFileCount = 0
}

async function makeRequestLocal(event) {
    toast.add({
      severity: "success",
      summary: "Request Local",
      detail: 'Local Upload...',
      life: 3000,
    });
    console.log(fileUpload.value)
    return
}

async function makeRequest(event) {
  const formData = new FormData();
  formData.append("acronym", acronym.value)
  formData.append("title", title.value);
  formData.append("paper_title", paperTitle.value);
  formData.append("author", author.value);
  formData.append("description", description.value);
  formData.append("doi", doi.value);
  formData.append("origins_doi", originsDoi.value);
  formData.append("submitter", JSON.stringify({
    name: name.value,
    email: email.value
  }));
  formData.append("tags", tags.value === undefined ? [] : tags.value);

  formData.append("file", event.files[0]);

  if (acronym.value.length == 0) {
    clearUpload()
    acronymError.value = true
    toast.add({
      severity: "error",
      summary: "Request Error",
      detail: 'Dataset Acronym is required.',
      life: 3000,
    });
    return
  }

  name.value = encodeURIComponent(name.value)

  await axios
    .post("/api/requests", formData, {
      headers: {
        'Content-Type': 'multipart/form-data', // Make sure to set the correct content type
      },
    })
    .then((response) => {
      console.log(response.data);
      dialogRef.value.close(acronym.value)
    })
    .catch((error) => {
      console.log(error)
      toast.add({
        severity: "error",
        summary: "Upload Error",
        detail: error.response.data.detail,
        life: 3000,
      });
      clearUpload()
    });
}

watch(acronym, (value) => {
  acronymError.value = value.length === 0
})

// watch(title, (value) => {
//   titleError.value = value.length === 0
// })

// watch(name, (value) => {
//   nameError.value = value.length === 0
// })

// watch(email, (value) => {
//   emailError.value = value.length === 0
// })

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
