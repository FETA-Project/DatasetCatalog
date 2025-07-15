<template>
  <div>
    <MainMenu />
    <h1 class="m-4 text-3xl font-bold">Users</h1>
    <ConfirmDialog />
    <DataTable
      :value="users"
      scrollable
      scrollHeight="500px"
      :filters="filters"
      v-model:selection="selectedData"
    >
      <Toast position="bottom-right" />
      <template #header>
        <div class="flex flex-wrap gap-2 items-center justify-between">
          <div>
            <Button
              v-if="current_user && current_user.is_admin"
              label="Delete"
              icon="pi pi-trash"
              severity="danger"
              @click="deleteData()"
              :disabled="!selectedData || !selectedData.length"
            />
          </div>
          <IconField>
            <InputIcon>
              <i class="pi pi-search" />
            </InputIcon>
            <InputText
              v-model="filters['global'].value"
              placeholder="Search..."
            />
          </IconField>
        </div>
      </template>
      <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
      <Column field="email" header="Email" sortable></Column>
      <Column field="name" header="Name"></Column>
      <Column field="surname" header="Surname"></Column>
      <Column field="created_at" header="Created At">
        <template #body="slotProps">
          <FormatedDate :datetime="slotProps.data.created_at" />
        </template>
      </Column>
      <Column field="is_admin" header="Role">
        <template #body="slotProps">
          <ToggleButton
            v-model="slotProps.data.is_admin"
            onLabel="Admin"
            offLabel="User"
            onIcon="pi pi-wrench"
            offIcon="pi pi-user"
            class="p-button-sm"
            :disabled="
              current_user.email == slotProps.data.email ||
              !current_user.is_admin
            "
            @change="updateAdminStatus(slotProps.data)"
          />
        </template>
      </Column>
    </DataTable>
    <DynamicDialog />
  </div>
</template>

<script setup>
import axios from "axios";
import MainMenu from "@/components/menu.vue";
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";
import { useDialog } from "primevue/usedialog";
import FormatedDate from "@/components/date.vue";

const router = useRouter();

const toast = useToast();
const confirm = useConfirm();
const dialog = useDialog();

const selectedData = ref([]);

const filters = ref({
  global: { value: null, matchMode: "contains" },
});

const current_user = ref(null);
const users = ref([]);
const is_admin = ref({});

const get_users = () => {
  axios
    .get("/api/users")
    .then((response) => {
      users.value = response.data;
    })
    .catch((error) => {
      toast.add({
        severity: "error",
        summary: "Error while getting requests",
        detail: error.response.data,
        life: 3000,
      });
    });

  users.value.forEach((user) => (is_admin.value[user.email] = user.is_admin));
  console.log(is_admin.value);
};

onMounted(() => {
  axios
    .get("/api/users/me")
    .then((response) => {
      console.log(response.data);
      current_user.value = response.data;
    })
    .catch();

  get_users();
});

const deleteData = () => {
  let to_delete = [];
  console.log(selectedData);
  selectedData.value.forEach((d) => {
    to_delete.push(d.email);
  });
  console.log(to_delete);
  confirm.require({
    message: `Are you sure you want to delete ${to_delete.length} users`,
    header: "Delete Confirmation",
    icon: "pi pi-exclemation-triangle",
    accept: () => {
      selectedData.value = null;
      to_delete.forEach((email) => {
        axios
          .delete(`/api/users/${email}`)
          .then(() => {
            toast.add({
              severity: "success",
              summary: "Delete Successful",
              detail: `User ${email} deleted successfully.`,
              life: 3000,
            });
            get_users();
          })
          .catch((error) => {
            toast.add({
              severity: "error",
              summary: "Delete Failed",
              detail: error.response.data,
              life: 3000,
            });
          });
      });
    },
  });
};

const updateAdminStatus = (user) => {
  const formData = new FormData();
  formData.append("is_admin", user.is_admin);
  axios
    .post(`/api/users/${user.email}/edit`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then((response) => {
      toast.add({
        severity: "success",
        summary: "User role changed",
        detail: `Updated user ${user.email} role to: ${
          user.is_admin ? "Admin" : "User"
        }`,
        life: 3000,
      });
    })
    .catch((error) => {
      toast.add({
        severity: "error",
        summary: "User role change failed",
        detail: `Failed to update user role for ${user.email}: ${error}`,
        life: 3000,
      });
    });
};
</script>
