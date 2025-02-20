<template>
  <div id="container" class="card flex justify-center">
    <div class="flex flex-col gap-4 container">
      <Toast position="bottom-right" />
      <div id="acronym" :class="{ error: acronymError }" class="flex flex-col gap-2">
        <label for="title">
            <i class="pi pi-info-circle" v-tooltip.right="'Short name of the dataset (e.g. CESNET-TLS22) which is used as the unique identifier'" />
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
      <div id="versions" class="flex flex-col gap-2">
        <label for="versions">
            <i class="pi pi-info-circle" v-tooltip.right="'Additional version for the Dataset Acronym (e.g. CESNET-TLS22-XS).\nUsed to filter the different subsection of the original dataset'" />
            Dataset Versions
        </label>
            <AutoComplete 
              id="versions"
              v-model="versions"
              placeholder="Versions..."
              aria-describedby="versions-help"
              :multiple="true"
              :typeahead="false"
              v-tooltip.bottom="'Versions.'"
              />
      </div>
      <div id="title" :class="{ error: titleError }" class="flex flex-col gap-2">
        <label for="title">
            <i class="pi pi-info-circle" v-tooltip.right="'Full name of the dataset'" />
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
      <div id="name" :class="{ error: nameError }" class="flex flex-col gap-2">
        <label for="name">
            <i class="pi pi-info-circle" v-tooltip.right="'Full name of the submitter'" />
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
      <div id="email" :class="{ error: emailError }" class="flex flex-col gap-2">
        <label for="email">
            <i class="pi pi-info-circle" v-tooltip.right="'Email of the submitter'" />
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
      <div id="paperTitle" :class="{ error: paperTitleError }" class="flex flex-col gap-2">
        <label for="paperTitle">
            <i class="pi pi-info-circle" v-tooltip.right="'Full title of the paper describing the dataset'" />
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
      <div id="datasetAuthors" :class="{ error: authorsError }" class="flex flex-col gap-2">
        <label for="authors">
            <i class="pi pi-info-circle" v-tooltip.right="'Authors of the dataset (comma separated)'" />
            Dataset Authors
        </label>
            <AutoComplete 
              id="authors"
              v-model="authors"
              placeholder="Authors..."
              aria-describedby="authors-help"
              :multiple="true"
              :typeahead="false"
              v-tooltip.bottom="'The dataset authors.'"
              />
        <small v-if="authorsError" class="p-error">
          <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
          Dataset Author is required.
        </small>
      </div>
      <div id="description" class="flex flex-col gap-2">
        <label for="Description">
            <i class="pi pi-info-circle" v-tooltip.right="'Short overview description of the dataset'" />
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
      <div id="format" class="flex flex-col gap-2">
        <label for="format">
            <i class="pi pi-info-circle" v-tooltip.right="'Identify file format of the dataset (e.g. pcap, json, txt, …)'" />
            Dataset Format
        </label>
        <InputText
                id="format"
                v-model="format"
                :class="{ error: formatError }"
                aria-describedby="format-help"
                placeholder="Format"
                /> 
      </div>
      <div id="label_name" class="flex flex-col gap-2">
        <label for="label_name">
            <i class="pi pi-info-circle" v-tooltip.right="'The Label'" />
            Dataset Label Name
        </label>
        <InputText
                id="label_name"
                v-model="label_name"
                :class="{ error: label_nameError }"
                aria-describedby="label_name-help"
                placeholder="Label Name"
                /> 
      </div>
      <div id="tags" class="flex flex-col gap-2">
        <label for="tags">
            <i class="pi pi-info-circle" v-tooltip.right="'Use tags to categorize the dataset (comma separated)'" />
            Tags
        </label>
            <AutoComplete 
              id="tags"
              v-model="tags"
              placeholder="Tags..."
              aria-describedby="tags-help"
              :multiple="true"
              :typeahead="false"
              v-tooltip.bottom="'Tags to describe the dataset.'"
              />
      </div>
      <div id="doi" class="flex flex-col gap-2">
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
      <div id="uploadLater" class="flex gap-2">
        <label for="uploadLater">
            <i class="pi pi-info-circle" v-tooltip.right="'Upload a file or URL later.'" />
            Upload Later
        </label>
        <Checkbox id="uploadLater" v-model="uploadLater" :binary="true" />
      </div>
      <Button v-if="uploadLater" label="Submit" icon="pi pi-upload" @click="makeRequest" />
      <TabView v-else id="dataset-upload">
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
              <p class="flex justify-center">
                Drag and drop file here to upload.
              </p>
            </template>
          </FileUpload>
        </TabPanel>
        <TabPanel header="URL">
            <div class="flex justify-center gap-2">
               <InputText
                id="url"
                v-model="url"
                aria-describedby="url-help"
                placeholder="URL"
                class="w-8/12"
                /> 
                <Button
                  label="Submit"
                  icon="pi pi-upload"
                  @click="makeRequest"
                  class="w-4/12"
                />
            </div>
        </TabPanel>
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
const versions = ref("");
const acronym_versionsError = ref(false);
const title = ref("");
const titleError = ref(false);
const paperTitle = ref("");
const paperTitleError = ref(false);
const authors = ref("");
const authorsError = ref(false);
const description = ref("");
const descriptionError = ref(false);
const format = ref("");
const formatError = ref(false);
const label_name = ref("");
const label_nameError = ref(false);
const doi = ref("");
const doiError = ref(false);
const name = ref("");
const nameError = ref(false);
// TODO: check if email is valid
const email = ref("");
const emailError = ref(false);
const url = ref("");
const urlError = ref(false);
const fileUpload = ref(null);
const tags = ref();
const uploadLater = ref(false);

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
  formData.append("versions", versions.value === undefined ? [] : versions.value);
  formData.append("title", title.value);
  formData.append("paper_title", paperTitle.value);
  formData.append("authors", authors.value === undefined ? [] : authors.value);
  formData.append("description", description.value);
  formData.append("format", format.value);
  formData.append("doi", doi.value);
  formData.append("submitter", JSON.stringify({
    name: name.value,
    email: email.value
  }));
  formData.append("tags", tags.value === undefined ? [] : tags.value);
  formData.append("url", url.value);
  formData.append("label_name", label_name.value);

  console.log(event.files)
  if(event.files !== undefined) {
      formData.append("file", event.files[0]);
  }

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

  formData.forEach(element => {
    console.log(element)
  });

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
