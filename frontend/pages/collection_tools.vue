<template>
  <div>
    <Toast position="bottom-right" />
    <MainMenu />
    <h1 class="m-4 text-3xl font-bold">Collection Tools</h1>
    <ConfirmDialog />
    <DataTable
      :value="tools"
      scrollable
      :filters="filters"
      v-model:selection="selectedData"
      v-model:expanded-rows="expandedRows"
    >
      <template #header>
        <div class="flex flex-wrap gap-2 items-center justify-between">
          <div>
            <Button
              label="Create Collection Tool"
              icon="pi pi-ticket"
              class="mr-2"
              @click="showUpload"
            />
            <Button
              v-if="user && user.is_admin"
              label="Delete"
              icon="pi pi-trash"
              class="mr-2"
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
      <Column expander style="width: 3rem"></Column>
      <Column field="name" header="Name" sortable></Column>
      <Column field="url" header="URL">
        <template #body="slotProps">
          <a :href="getURL(slotProps.data.url)" about="_blank">{{
            slotProps.data.url
          }}</a>
        </template>
      </Column>
      <Column>
        <template #body="slotProps">
          <Button
            v-if="user && user.is_admin"
            @click="editTool(slotProps.data)"
            label="Edit"
            icon="pi pi-pencil"
            rounded
            outlined
          />
        </template>
      </Column>
      <template #expansion="slotProps">
        <div class="flex">
          <ul style="list-style: none">
            <li><b>Description: </b> {{ slotProps.data.description }}</li>
            <br />
            <li><b>Known Issues: </b> {{ slotProps.data.known_issues }}</li>
          </ul>
        </div>
      </template>
    </DataTable>
    <DynamicDialog />
  </div>
</template>

<script setup>
import axios from "axios";
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";
import MainMenu from "@/components/menu.vue";
import { useDialog } from "primevue/usedialog";
import FormatedDate from "@/components/date.vue";

const router = useRouter();

const confirm = useConfirm();
const toast = useToast();
const dialog = useDialog();

const user = ref(null);

const selectedData = ref([]);
const expandedRows = ref([]);

const filters = ref({
  global: { value: null, matchMode: "contains" },
});

const tools = ref([]);

const UploadDialog = defineAsyncComponent(() =>
  import("../components/create_tool.vue")
);
const EditDialog = defineAsyncComponent(() =>
  import("../components/edit_tool.vue")
);

const get_tools = () => {
  //   datasets.value = fake_data
  //   return
  axios
    .get("/api/collectionTools")
    .then((response) => {
      tools.value = response.data;
    })
    .catch((error) => {
      toast.add({
        severity: "error",
        summary: "Error while getting datasets",
        detail: error.response.data,
        life: 3000,
      });
    });
};

onMounted(() => {
  get_tools();
});

const getURL = (url, open = false) => {
  let _url = url;
  if (!/^https?:\/\//i.test(url)) {
    (_url = `https://${url}`), "_blank";
  }

  return open ? window.open(_url, "_blank") : _url;
};

const showDetail = (acronym, versions) => {
  console.log(acronym, versions);
  if (versions == "") {
    versions = "*";
  }
  navigateTo(
    `/detail/${encodeURIComponent(acronym)}/${encodeURIComponent(versions)}`
  );
};

const deleteData = () => {
  let to_delete = [];
  selectedData.value.forEach((d) => {
    to_delete.push({ name: d.name });
  });
  confirm.require({
    message: `Are you sure you want to delete ${to_delete.length} collection tools`,
    header: "Delete Confirmation",
    icon: "pi pi-exclemation-triangle",
    accept: () => {
      selectedData.value = null;
      to_delete.forEach((d) => {
        axios
          .delete(`/api/collectionTools/${encodeURIComponent(d.name)}`)
          .then(() => {
            toast.add({
              severity: "success",
              summary: "Delete Successful",
              detail: `Collection tool ${d.name} deleted successfully.`,
              life: 3000,
            });
            get_tools();
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

const showUpload = () => {
  const dialogRef = dialog.open(UploadDialog, {
    props: {
      header: "Create Collection Tool",
      modal: true,
    },
    onClose: (options) => {
      console.log("Dialog closed: " + options);
      get_tools();
    },
  });
};

const editTool = (tool) => {
  const dialogRef = dialog.open(EditDialog, {
    props: {
      header: "Edit Collection Tool",
      modal: true,
    },
    data: {
      name: tool.name,
      description: tool.description,
      known_issues: tool.known_issues,
      url: tool.url,
    },
    onClose: () => {
      get_tools();
    },
  });
};

onMounted(() => {
  axios
    .get("/api/users/me")
    .then((response) => {
      user.value = response.data;
    })
    .catch();
});
</script>
