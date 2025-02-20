<template>
  <div>
    <Toast position="bottom-right" />
    <MainMenu />
    <h1 class="m-4 text-3xl font-bold">Dataset Catalog</h1>
    <ConfirmDialog />
    <DataTable :value="datasets" scrollable :filters="filters"
            v-model:selection="selectedData"
            v-model:expanded-rows="expandedRows">
    <template #header>
        <div class="flex flex-wrap gap-2 items-center justify-between">
            <div>
                <Button label="Submit Dataset" icon="pi pi-ticket" class="mr-2" @click="showUpload" />
                <Button v-if="user && user.is_admin" label="Delete" icon="pi pi-trash" class="mr-2" severity="danger" @click="deleteData()" :disabled="!selectedData || !selectedData.length" />
            </div>
            <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText v-model="filters['global'].value" placeholder="Search..." />
            </span>
        </div>
    </template>
    <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
    <Column expander style="width: 3rem"></Column>
    <Column field="metadata" header="Metadata" hidden></Column>
    <Column field="acronym" header="Acronym" sortable></Column>
    <Column field="versions" header="Versions" sortable.multiple>
      <template #body="slotProps">
        <div class="flex gap-1" v-if="slotProps.data.versions.length > 1 || slotProps.data.versions[0] != ''">
            <Chip v-for="version in slotProps.data.versions" :label="version"></Chip>
        </div>
      </template>
    </Column>
    <Column field="title" header="Title" sortable></Column>
    <Column field="doi" header="DOI">
        <template #body="slotProps">
            <a :href="'https://doi.org/' + slotProps.data.doi" target="_blank">{{ slotProps.data.doi }}</a>
        </template>
    </Column>
    <Column field="tags" header="Tags">
      <template #body="slotProps">
        <div class="flex gap-1" v-if="slotProps.data.tags.length > 1 || slotProps.data.tags[0] != ''">
            <Chip v-for="tag in slotProps.data.tags" :label="tag"></Chip>
        </div>
      </template>
    </Column>
    <Column field="analysis_status" header="Analysis Status">
      <template #body="slotProps">
        <div class="flex gap-1">
            <Chip :label="slotProps.data.analysis_status"></Chip>
        </div>
      </template>
    </Column>
    <Column>
        <template #body="slotProps">
            <Button @click="showDetail(slotProps.data.acronym, slotProps.data.versions)" label="Details" icon="pi pi-info-circle" rounded outlined />
        </template>
    </Column>
    <template #expansion="slotProps">
        <div class="flex">
            <ul style="list-style: none" v-if="slotProps.data.children.length > 0">
                <li> <b>Children:</b>
                    <ul>
                        <li v-for="child in slotProps.data.children">
                            <span class="detail-link" @click="showDetail(child.acronym, child.versions)">{{ child.acronym+'['+child.versions+']'}}</span>
                        </li>
                    </ul>
                </li>
            </ul>
        </div>
        <div class="flex">
            <ul style="list-style: none">
                <li><b>Paper Title: </b> {{ slotProps.data.paper_title }}</li>
                <li class="flex gap-2"> <b>Authors: </b> 
                    <div class="flex gap-1" v-if="slotProps.data.authors.length > 1 || slotProps.data.authors[0] != ''">
                        <Chip v-for="author in slotProps.data.authors">{{ author }}</Chip>
                    </div>
                </li>
                <li><b>Date Submitted: </b> <FormatedDate :datetime="slotProps.data.date_submitted"/></li>
                <li>
                    <b>Submitter: </b>
                    <ul>
                        <li><b>Name: </b> {{ slotProps.data.submitter.name }}</li>
                        <li><b>Email: </b> {{ slotProps.data.submitter.email}}</li>
                    </ul>
                </li>
                <li> <b>Description: </b> {{ slotProps.data.description }} </li>
            </ul>
        </div>
    </template>
    </DataTable>
    <DynamicDialog />
  </div>
</template>

<script setup>
import axios from 'axios'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import MainMenu from '@/components/menu.vue'
import { useDialog } from 'primevue/usedialog'
import FormatedDate from '@/components/date.vue'

const router = useRouter()

const confirm = useConfirm()
const toast = useToast()
const dialog = useDialog()

const user = ref(null)

const selectedData = ref([])
const expandedRows = ref([])

const filters = ref({
    'global': {value: null, matchMode: "contains"}
})

const datasets = ref([])

const UploadDialog = defineAsyncComponent(() => import('../components/upload.vue'))

const get_datasets = () => {
//   datasets.value = fake_data
//   return
  axios.get('/api/datasets')
    .then(response => {
        console.log(response.data)
      datasets.value = response.data.filter(d => d.parents.length == 0)
      console.log(datasets.value)
      datasets.value.forEach(d => {
          // add metadata to datasets, replace underscores with spaces in keys
          d.metadata = JSON.stringify(d, function (key, value) {
              if (value && typeof value === 'object') {
                var replacement = {};
                for (var k in value) {
                  if (Object.hasOwnProperty.call(value, k)) {
                    replacement[k && k.replaceAll("_", " ")] = value[k];
                  }
                }
                return replacement;
              }
              return value;
            });
      })
    //   console.log(datasets.value)
    })
    .catch(error => {
      toast.add({
        severity: 'error',
        summary: 'Error while getting datasets',
        detail: error.response.data,
        life: 3000
      })
    })
}

onMounted(() => {
    get_datasets()
})

const showDetail = (acronym, versions) => {
    console.log(acronym, versions)
    if(versions == "") {
        versions = "*"
    }
    navigateTo(`/detail/${encodeURIComponent(acronym)}/${encodeURIComponent(versions)}`)
}

const deleteData = () => {
    let to_delete = []
    selectedData.value.forEach(d => {
        to_delete.push({'acronym': d.acronym, 'versions': d.versions})
    });
    confirm.require({
        message: `Are you sure you want to delete ${to_delete.length} files`,
        header: 'Delete Confirmation',
        icon: 'pi pi-exclemation-triangle',
        accept: () => {
            selectedData.value = null
            to_delete.forEach(d => {
                axios.delete(`/api/datasets/${encodeURIComponent(d.acronym)}/${encodeURIComponent(d.versions)}`)
                    .then(() => {
                        toast.add({
                            severity: 'success',
                            summary: 'Delete Successful',
                            detail: `Dataset ${d.acronym}/${d.versions} deleted successfully.`,
                            life: 3000
                            })
                        get_datasets()
                    })
                    .catch((error) => {
                        toast.add({
                            severity: 'error',
                            summary: 'Delete Failed',
                            detail: error.response.data,
                            life: 3000
                        })
                    })
            })
        }
    })
}

const showUpload = () => {
    const dialogRef = dialog.open(UploadDialog, {
        props: {
            header: 'Submit Dataset',
            modal: true
        },
        onClose: (options) => {
            const uploadedFile = options.data
            if (uploadedFile) {
                toast.add({
                    severity: 'success',
                    summary: 'Upload Successful',
                    detail: `File ${uploadedFile} uploaded successfully.`,
                    life: 3000
                })
                get_datasets()
            }
        }
    })
}

onMounted(() => { 
    axios.get('/api/users/me')
    .then(response => {
        user.value = response.data
    })
    .catch()
})
</script>

<style>
.body {
    font-size: 0.8rem;
}
.detail-link {
  cursor: pointer;
  text-decoration: dotted underline;
}
</style>