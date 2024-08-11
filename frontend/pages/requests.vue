<template>
    <div>
        <MainMenu />
        <h1>
            Requested For Analysis
        </h1>
        <ConfirmDialog />
        <DataTable :value="requests" scrollable scrollHeight="500px" :filters="filters"
                v-model:selection="selectedData">
        <Toast position="bottom-right" />
        <template #header>
            <div class="flex flex-wrap gap-2 align-items-center justify-content-between">
                <div>
                    <Button label="Submit Dataset" icon="pi pi-ticket" class="mr-2" @click="showUpload" />
                    <Button label="Approve" icon="pi pi-check" severity="success" class="mr-2"
                        @click="approveRequest()" :disabled="!selectedData || !selectedData.length"/>
                    <Button label="Reject" icon="pi pi-ban" severity="danger"
                        @click="rejectRequest()" :disabled="!selectedData || !selectedData.length" />
                </div>
                <span class="p-input-icon-left">
                    <i class="pi pi-search" />
                    <InputText v-model="filters['global'].value" placeholder="Search..." />
                </span>
            </div>
        </template>
        <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
        <Column field="acronym" header="Dataset Acronym" sortable></Column>
        <Column field="title" header="Dataset Title" sortable></Column>
        <Column field="submitter.name" header="Submitter Name"></Column>
        <Column field="submitter.email" header="Submitter Email"></Column>
        <Column>
            <template #body="slotProps">
                <Button @click="showDetail(slotProps.data.acronym)" label="Details" icon="pi pi-info-circle" rounded outlined />
            </template>
        </Column>
        </DataTable>
        <DynamicDialog />
    </div>
</template>

<script setup>
import axios from 'axios'
import { FilterMatchMode } from 'primevue/api'
import MainMenu from '@/components/menu.vue'
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm'
import { useDialog } from 'primevue/usedialog'

const router = useRouter()

const toast = useToast()
const confirm = useConfirm()
const dialog = useDialog()

const selectedData = ref([])

const UploadDialog = defineAsyncComponent(() => import('../components/upload.vue'))

const filters = ref({
    'global': {value: null, matchMode: FilterMatchMode.CONTAINS}
})

const requests = ref([])

const get_requests = () => {
    axios.get('/api/requests')
    .then(response => {
        requests.value = response.data
    })
    .catch(error => {
      toast.add({
        severity: 'error',
        summary: 'Error while getting requests',
        detail: error.response.data,
        life: 3000
      })
    })
}

onMounted(() => get_requests())

const rejectRequest = () => {
    let to_reject = []
    selectedData.value.forEach(d => {
        to_reject.push(d.title)
    });
    console.log(to_reject)

    confirm.require({
        message: `Are you sure you want to reject ${to_reject.length} datasets?`,
        header: 'Reject Confirmation',
        icon: 'pi pi-exclemation-triangle',
        accept: () => {
            selectedData.value = null
            to_reject.forEach(title => {
                axios.delete(`/api/requests/${title}`)
                    .then(() => {
                        toast.add({
                            severity: 'success',
                            summary: 'Rejection Successful',
                            detail: `Dataset ${title} rejected.`,
                            life: 3000
                            })
                        get_requests()
                    })
                    .catch((error) => {
                        toast.add({
                            severity: 'error',
                            summary: 'Error while rejecting request',
                            detail: error.response.data,
                            life: 3000
                        })
                    })
            })
        }
    })
}

const approveRequest = () => {
    let to_approve = []
    selectedData.value.forEach(d => {
        to_approve.push(d.title)
    });
    console.log(to_approve)

    to_approve.forEach(title => {
        axios.head(`/api/requests/${title}`)
            .then(() => {
                toast.add({
                    severity: 'success',
                    summary: 'Approval Successful',
                    detail: `Request ${title} approved.`
                })
                get_requests()
            })
            .catch((error) => {
                // FIXME: error.response.data
                toast.add({
                    severity: 'error',
                    summary: 'Error while accepting request',
                    detail: error.response.data,
                    life: 3000
                })
            })
    })
}

const showDetail = (acronym) => {
    navigateTo(`/detail/${encodeURIComponent(acronym)}`)
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
                get_requests()
            }
        }
    })
}

</script>