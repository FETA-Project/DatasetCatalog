<template>
    <div>
        <MainMenu />
        <h1 class="m-4 text-3xl font-bold">
            Users
        </h1>
        <ConfirmDialog />
        <DataTable :value="users" scrollable scrollHeight="500px" :filters="filters"
                v-model:selection="selectedData">
        <Toast position="bottom-right" />
        <template #header>
            <div class="flex flex-wrap gap-2 items-center justify-between">
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
        <Column field="email" header="Email" sortable></Column>
        <Column field="name" header="Name"></Column>
        <Column field="surname" header="Surname"></Column>
        <Column field="created_at" header="Created At"></Column>
        <Column field="is_admin" header="Is Admin"></Column>
        </DataTable>
        <DynamicDialog />
    </div>
</template>

<script setup>
import axios from 'axios'
import MainMenu from '@/components/menu.vue'
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm'
import { useDialog } from 'primevue/usedialog'

const router = useRouter()

const toast = useToast()
const confirm = useConfirm()
const dialog = useDialog()

const selectedData = ref([])

const filters = ref({
    'global': {value: null, matchMode: "contains"}
})

const users = ref([])

const get_users = () => {
    axios.get('/api/users')
    .then(response => {
        users.value = response.data
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

onMounted(() => get_users())

const deleteData = () => {
    let to_delete = []
    console.log(selectedData)
    selectedData.value.forEach(d => {
        to_delete.push(d.email)
    });
    console.log(to_delete)
    confirm.require({
        message: `Are you sure you want to delete ${to_delete.length} users`,
        header: 'Delete Confirmation',
        icon: 'pi pi-exclemation-triangle',
        accept: () => {
            selectedData.value = null
            to_delete.forEach(email => {
                axios.delete(`/api/users/${email}`)
                    .then(() => {
                        toast.add({
                            severity: 'success',
                            summary: 'Delete Successful',
                            detail: `User ${email} deleted successfully.`,
                            life: 3000
                            })
                        get_users()
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

</script>