<template>
  <div>
    <Toast position="bottom-right" />
    <MainMenu />
    <h1>Dataset Catalog</h1>
    <ConfirmDialog />
    <DataTable :value="datasets" scrollable :filters="filters"
            v-model:selection="selectedData"
            v-model:expanded-rows="expandedRows">
    <template #header>
        <div class="flex flex-wrap gap-2 align-items-center justify-content-between">
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
    <Column field="acronym_aliases" header="Acronym Aliases" sortable.multiple>
      <template #body="slotProps">
        <div class="flex gap-1">
            <Chip v-for="alias in slotProps.data.acronym_aliases" :label="alias"></Chip>
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
        <div class="flex gap-1">
            <Chip v-for="tag in slotProps.data.tags" :label="tag"></Chip>
        </div>
      </template>
    </Column>
    <Column>
        <template #body="slotProps">
            <Button @click="showDetail(slotProps.data.acronym, slotProps.data.acronym_aliases)" label="Details" icon="pi pi-info-circle" rounded outlined />
        </template>
    </Column>
    <template #expansion="slotProps">
        <div class="flex">
            <ul style="list-style: none">
                <li><b>Paper Title: </b> {{ slotProps.data.paper_title }}</li>
                <li class="flex gap-2"> <b>Authors: </b> 
                    <Chip v-for="author in slotProps.data.authors">{{ author }}</Chip>
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
                <li> <b>Origins: </b> <a :href="slotProps.data.origins_doi" target="_blank">{{ slotProps.data.origins_doi }}</a></li>
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
import { FilterMatchMode } from 'primevue/api'
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
    'global': {value: null, matchMode: FilterMatchMode.CONTAINS}
})

const datasets = ref([])

const UploadDialog = defineAsyncComponent(() => import('../components/upload.vue'))

const get_datasets = () => {
//   datasets.value = fake_data
//   return
  axios.get('/api/datasets')
    .then(response => {
      datasets.value = response.data
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

const showDetail = (acronym, aliases) => {
    console.log(acronym, aliases)
    if(aliases == "") {
        aliases = acronym
    }
    navigateTo(`/detail/${encodeURIComponent(acronym)}/${encodeURIComponent(aliases)}`)
}

const deleteData = () => {
    let to_delete = []
    selectedData.value.forEach(d => {
        to_delete.push({'acronym': d.acronym, 'aliases': d.acronym_aliases})
    });
    confirm.require({
        message: `Are you sure you want to delete ${to_delete.length} files`,
        header: 'Delete Confirmation',
        icon: 'pi pi-exclemation-triangle',
        accept: () => {
            selectedData.value = null
            to_delete.forEach(d => {
                axios.delete(`/api/datasets/${encodeURIComponent(d.acronym)}/${encodeURIComponent(d.aliases)}`)
                    .then(() => {
                        toast.add({
                            severity: 'success',
                            summary: 'Delete Successful',
                            detail: `Dataset ${d.acronym}/${d.aliases} deleted successfully.`,
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
