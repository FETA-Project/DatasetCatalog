<template>
  <div>
    <Toast position="bottom-right" />
    <MainMenu />
    <h1>Dataset Catalog</h1>
    <ConfirmDialog />
    <DataTable :value="datasets" scrollable scrollHeight="500px" :filters="filters"
            v-model:selection="selectedData"
            v-model:expanded-rows="expandedRows">
    <template #header>
        <div class="flex flex-wrap gap-2 align-items-center justify-content-between">
            <div>
                <Button label="Delete" icon="pi pi-trash" severity="danger" @click="deleteData()" :disabled="!selectedData || !selectedData.length" />
            </div>
            <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText v-model="filters['global'].value" placeholder="Search..." />
            </span>
        </div>
    </template>
    <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
    <Column expander style="width: 3rem"></Column>
    <Column field="title" header="Title" sortable></Column>
    <Column header="DOI">
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
            <Button @click="getDetails(slotProps.data.title)" label="Details" icon="pi pi-info-circle" rounded outlined />
        </template>
    </Column>
    <!-- <Column field="size" header="Size"></Column>
    <Column field="format" header="Format"></Column>
    <Column field="score" header="Score"></Column> -->
    <template #expansion="slotProps">
        <div class="flex justify-content-center">
            <ul style="list-style: none">
                <li>
                    <b>Requester</b>
                    <ul>
                        <li><b>Name:</b> {{ slotProps.data.requester.name }}</li>
                        <li><b>Email:</b> {{ slotProps.data.requester.email}}</li>
                    </ul>
                </li>
                <li> <b>Description:</b> {{ slotProps.data.description }} </li>
                <li> <b>Date:</b> {{ slotProps.data.date }}</li>
                <!-- <li> <b>Date:</b> <Date timedate="{{ slotProps.data.date }}" /> </li> -->
                <li> <b>Origins DOI:</b> 
                    <ul>
                        <li v-for="value in slotProps.data.origins_doi">
                            <a :href="'https://doi.org/' + value" target="_blank">{{ value }}</a>
                        </li>
                    </ul>
                </li>
            </ul>
        </div>
    </template>
    </DataTable>
  </div>
</template>

<script setup>
import axios from 'axios'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { FilterMatchMode } from 'primevue/api'
import MainMenu from '@/components/menu.vue'
import Date from '@/components/date.vue'

const router = useRouter()

const confirm = useConfirm()
const toast = useToast()

const selectedData = ref([])
const expandedRows = ref([])

const filters = ref({
    'global': {value: null, matchMode: FilterMatchMode.CONTAINS}
})

const datasets = ref([])

const get_datasets = () => {
//   datasets.value = fake_data
//   return
  axios.get('/api/datasets')
    .then(response => {
      datasets.value = response.data
      console.log(datasets.value)
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

onMounted(() => get_datasets())

const getDetails = (title) => {
    router.push({ path: `/detail/${title}` })
}

const deleteData = () => {
    let to_delete = []
    selectedData.value.forEach(d => {
        to_delete.push(d.title)
    });
    confirm.require({
        message: `Are you sure you want to delete ${to_delete.length} files`,
        header: 'Delete Confirmation',
        icon: 'pi pi-exclemation-triangle',
        accept: () => {
            selectedData.value = null
            to_delete.forEach(title => {
                axios.delete(`/api/datasets/${title}`)
                    .then(() => {
                        toast.add({
                            severity: 'success',
                            summary: 'Delete Successful',
                            detail: `Dataset ${title} deleted successfully.`,
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
const fake_data = [
    {
        title: "Name",
        requester: {
            name: "test1",
            email: "test1"
        },
        description: "test1",
        location: "test1",
        tags: ["test1"],
        report: {
            Classes: 0,
            'Duplicated Flows': 0,
            Features: 0,
            Redundancy: 0.0,
            Samples : [0]
        }
    },
]

</script>
