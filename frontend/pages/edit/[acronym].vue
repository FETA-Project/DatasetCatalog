<template>
    <div class="flex flex-column gap-3">
        <Toast position="bottom-right" />
        <MainMenu />
      <div id="container" class="card flex justify-content-center">
        <div class="flex flex-column gap-3 container">
          <Toast position="bottom-right" />
        <h1>
            Editing {{ dataset_acronym }}
        </h1>
          <!-- <div id="acronym" :class="{ error: acronymError }" class="flex flex-column gap-2">
            <label for="title">
                <i class="pi pi-info-circle" v-tooltip.right="'Acronym of the dataset'" />
                Dataset Acronym*
            </label>
            <InputText
              :readonly="true"
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
          </div> -->
          <div id="acronym_alias" :class="{ error: acronym_aliasesError }" class="flex flex-column gap-2">
            <label for="acronym_alias">
                <i class="pi pi-info-circle" v-tooltip.right="'The acronym aliases.'" />
                Dataset Acronym Aliases
            </label>
            <div class="card p-fluid p-hidden-label">
                <Chips 
                  id="acronym_aliases"
                  v-model="acronym_aliases"
                  separator=","
                  placeholder="Aliases..."
                  add-on-blur="true"
                  allow-duplicate="false"
                  v-tooltip.bottom="'The dataset acronym aliases.'"
                />
            </div>
            <small v-if="acronym_aliasesError" class="p-error">
              <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
              Dataset Aliases are required.
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
          <div id="author" :class="{ error: authorsError }" class="flex flex-column gap-2">
            <label for="author">
                <i class="pi pi-info-circle" v-tooltip.right="'Title of the dataset'" />
                Dataset Authors
            </label>
            <div class="card p-fluid p-hidden-label">
                <Chips 
                  id="authors"
                  v-model="authors"
                  separator=","
                  placeholder="Authors..."
                  add-on-blur="true"
                  allow-duplicate="false"
                  v-tooltip.bottom="'The dataset authors.'"
                />
            </div>
            <small v-if="authorsError" class="p-error">
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
          <div id="url" :class="{ error: urlError }" class="flex flex-column gap-2">
            <label for="url">
                <i class="pi pi-info-circle" v-tooltip.right="'Title of the dataset'" />
                Dataset File URL
            </label>
            <InputText
              id="url"
              v-model="url"
              aria-describedby="url-help"
              placeholder="Dataset Title"
            />
            <!-- <small v-if="urlError" class="p-error">
              <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
              Dataset Title is required.
            </small> -->
          </div>
          <footer>
            <Button label="Edit" icon="pi pi-pencil" class="mr-2" @click="editDataset()"/>
          </footer>
          <!-- <footer><small>* required field</small></footer> -->
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import MainMenu from '@/components/menu.vue'
import axios from "axios";


const router = useRouter();
const route = useRoute();

const toast = useToast();

const dialogRef = inject("dialogRef")

const dataset_acronym = ref("");
const dataset = ref();

const acronym = ref("");
const acronymError = ref(false);
const acronym_aliases = ref("");
const acronym_aliasesError = ref(false);
const title = ref("");
const titleError = ref(false);
const paperTitle = ref("");
const paperTitleError = ref(false);
const authors = ref("");
const authorsError = ref(false);
const description = ref("");
const descriptionError = ref(false);
const doi = ref("");
const doiError = ref(false);
const originsDoi = ref("");
const originsDoiError = ref(false);
const name = ref("");
const nameError = ref(false);
const url = ref("");
const urlError = ref(false);
// TODO: check if email is valid
const email = ref("");
const emailError = ref(false);
const tags = ref();


watch(acronym, (value) => {
  acronymError.value = value.length === 0
})

const get_dataset = (_acronym) => {
    axios.get(`/api/datasets/${encodeURIComponent(_acronym)}`)
      .then(response => {
          dataset.value = response.data.dataset
          console.log(dataset.value)

          acronym.value = dataset.value.acronym
          acronym_aliases.value = dataset.value.acronym_aliases.filter(alias => alias !== "")
          title.value = dataset.value.title
          paperTitle.value = dataset.value.paper_title
          authors.value = dataset.value.authors.filter(author => author !== "")
          description.value = dataset.value.description
          doi.value = dataset.value.doi
          originsDoi.value = dataset.value.origins_doi
          name.value = dataset.value.submitter.name
          email.value = dataset.value.submitter.email
          tags.value = dataset.value.tags.filter(tag => tag !== "")
          url.value = dataset.value.url
      })
      .catch(error => {
            toast.add({
                severity: 'error',
                summary: 'Error while getting dataset',
                detail: error.response.data,
                life: 3000
            })
      })
}

async function editDataset() {
  const formData = new FormData();
//   formData.append("acronym", acronym.value)
  formData.append("acronym_aliases", acronym_aliases.value === undefined ? [] : acronym_aliases.value);
  formData.append("title", title.value);
  formData.append("paper_title", paperTitle.value);
  formData.append("authors", authors.value === undefined ? [] : authors.value);
  formData.append("description", description.value);
  formData.append("doi", doi.value);
  formData.append("origins_doi", originsDoi.value);
  formData.append("submitter", JSON.stringify({
    name: name.value,
    email: email.value
  }));
  formData.append("tags", tags.value === undefined ? [] : tags.value);

  await axios
    .post(`/api/datasets/${encodeURIComponent(dataset_acronym.value)}/edit`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data', // Make sure to set the correct content type
      },
    })
    .then(() => {
      navigateTo(`/detail/${encodeURIComponent(dataset_acronym.value)}`)
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

onMounted(() => { 
    // dataset_title.value = "dataset_example_name"
    dataset_acronym.value = decodeURIComponent(route.params.acronym)
    get_dataset(dataset_acronym.value)
})

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
