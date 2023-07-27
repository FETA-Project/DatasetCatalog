<template>
  <div id="container" class="card flex justify-content-center">
    <div class="flex flex-column gap-2 container">
      <Toast position="bottom-right" />
      <InputText
        id="title"
        v-model="title"
        :class="{ error: titleError }"
        aria-describedby="title-help"
        placeholder="Title"
        @blur="titleError = title.length === 0"
      />
      <small v-if="titleError" class="p-error">
        <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
        Title is required.
      </small>
      <InputText
        id="name"
        v-model="name"
        :class="{ error: nameError }"
        aria-describedby="name-help"
        placeholder="Name"
        @blur="nameError = name.length === 0"
      />
      <small v-if="nameError" class="p-error">
        <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
        Name is required.
      </small>
      <InputText
        id="email"
        v-model="email"
        :class="{ error: emailError }"
        aria-describedby="email-help"
        placeholder="Email"
        @blur="emailError = email.length === 0"
        />
      <TextArea
        id="description"
        v-model="description"
        aria-describedby="description-help"
        placeholder="Description..."
        rows="5"
        cols="30"
      />
      <div class="card p-fluid p-hidden-label">
          <Chips id="tags" v-model="tags" separator="," placeholder="Tag" />
      </div>
      <TabView>
        <TabPanel header="DOI">
            <div class="flex justify-content-center gap-2">
               <InputText
                id="doi"
                v-model="doi"
                :class="{ error: doiError }"
                aria-describedby="doi-help"
                placeholder="DOI or URL"
                @blur="doiError = doi.length === 0"
                class="w-8"
                /> 
                <Button
                  label="Request"
                  icon="pi pi-upload"
                  @click="makeRequestDOI"
                  class="w-4"
                />
            </div>
        </TabPanel>
        <TabPanel header="Local File">
          <FileUpload
            name="upload"
            :auto="false"
            :multiple="false"
            :fileLimit="1"
            custom-upload
            ref="fileUpload"
            @uploader="makeRequestLocal"
            upload-label="Request"
          >
            <template #empty>
              <p class="flex justify-content-center">
                Drag and drop file here to upload.
              </p>
            </template>
          </FileUpload>
        </TabPanel>
      </TabView>
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

const title = ref("");
const titleError = ref(false);
const name = ref("");
const nameError = ref(false);
const description = ref("");
// TODO: check if email is valid
const email = ref("");
const emailError = ref(false);
const doi = ref("");
const doiError = ref(false);
const fileUpload = ref(null);
const tags = ref();

watch(title, (value) => {
  titleError.value = value.length === 0;
});

watch(name, (value) => {
  nameError.value = value.length === 0;
});

watch(email, (value) => {
  emailError.value = value.length === 0;
});

watch(doi, (value) => {
  doiError.value = value.length === 0;
});

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
    return
}

async function makeRequestDOI(event) {
  const formData = new FormData();
  formData.append("title", title.value);
  formData.append("requester_name", name.value);
  formData.append("requester_email", email.value);
  formData.append("description", description.value);
  formData.append("doi", doi.value);
  formData.append("tags", tags.value);
  console.log(formData)
//   formData.append("file", event.files[0]);

  if (name.value.length == 0) {
    clearUpload()
    nameError.value = true
    toast.add({
      severity: "error",
      summary: "Request Error",
      detail: 'Name is required.',
      life: 3000,
    });
    return
  }

  await axios
    .post("/api/requests", formData)
    .then((response) => {
      console.log(response.data);
      dialogRef.value.close(name.value)
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
</script>

<style scoped>

.container {
    width: 30em;
}
.error {
  border-color: red;
}
</style>
