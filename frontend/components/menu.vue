<template>
  <div class="card relative z-20">
    <Menubar :model="items">
      <template #start>
        <div
          class="flex items-center cursor-pointer transition duration-200 rounded-md px-2 py-1"
          @click="navigateTo('/')"
        >
          <img :src="Logo" alt="Logo" class="h-10 w-30" />
        </div>
      </template>
      <template #end>
        <Button
          :icon="darkModeIcon"
          @click="toggleDarkMode()"
          class="p-button-rounded p-button-text **ml-2 px-3 py-2 text-black text-lg dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700**"
        />
        |
        <Button
          text
          plain
          severity="danger"
          label="Logout"
          @click="logout_shib()"
        />
      </template>
    </Menubar>
    <DynamicDialog />
  </div>
</template>

<script setup>
import axios from "axios";
import { useDialog } from "primevue/usedialog";
import LogoBlack from "~/assets/logo/katoda_horizontal_black.svg";
import LogoWhite from "~/assets/logo/katoda_horizontal_white.svg";

const user = ref(null);

onMounted(() => {
  axios
    .get("/api/users/me")
    .then((response) => {
      //   console.log(response.data);
      user.value = response.data;
      localStorage.setItem("user", response.data);
    })
    .catch();
});

// FIXME: get user from shibboleth
// const logged_in = () => user.value !== null
// const is_admin = () => user.value.is_admin
const logged_in = () => true;
const is_admin = () => true;

const items = ref([
  //   {
  //     label: "Catalog",
  //     icon: "pi pi-fw pi-home",
  //     command: () => navigateTo("/"),
  //   },
  logged_in() && is_admin()
    ? {
        label: "Users",
        icon: "pi pi-fw pi-users",
        command: () => navigateTo("/users"),
      }
    : null,
  {
    label: "Collection Tools",
    icon: "pi pi-fw pi-search",
    command: () => navigateTo("/collection_tools"),
    meta: {
      title: "Collection Tools",
    },
  },
  {
    label: "How to Use",
    icon: "pi pi-fw pi-info-circle",
    command: () => navigateTo("/howto"),
    meta: {
      title: "How to Use",
    },
  },
]);

const dialog = useDialog();
const LoginDialog = defineAsyncComponent(() =>
  import("../components/login.vue")
);

const darkModeIcon = ref("pi pi-fw pi-moon");
const Logo = ref(LogoBlack);

onMounted(() => {
  if (localStorage.getItem("darkMode") === "true") {
    document.documentElement.classList.add("dark");
    darkModeIcon.value = "pi pi-fw pi-sun";
    Logo.value = LogoWhite;
  }
});

function toggleDarkMode() {
  document.documentElement.classList.toggle("dark");

  if (document.documentElement.classList.contains("dark")) {
    localStorage.setItem("darkMode", "true");
    darkModeIcon.value = "pi pi-fw pi-sun";
    Logo.value = LogoWhite;
  } else {
    localStorage.removeItem("darkMode");
    darkModeIcon.value = "pi pi-fw pi-moon";
    Logo.value = LogoBlack;
  }
}

const login = () => {
  const dialogRef = dialog.open(LoginDialog, {
    props: {
      header: "Login",
      modal: true,
      // title: title,
    },
  });
};

const logout = () => {
  axios.get("/auth/logout").then((response) => {
    console.log(response);
    localStorage.removeItem("user");
    location.replace("/");
  });
};

const logout_shib = () => {
  document.cookie = "authToken=; Max-Age=0; Path=/;";

  // Redirect to the backend endpoint for Shibboleth logout
  //   navigateTo("/Shibboleth.sso/Logout?return=/logged-out");
  window.location.href = "/Shibboleth.sso/Logout?return=/logged-out";
  //   "/Shibboleth.sso/Logout?return=https://dataset-catalog.liberouter.org/logged-out";
};
</script>

<style scoped>
/* Custom CSS to right-align the end slot */
.p-menubar .p-menubar-end {
  justify-content: flex-end;
}
</style>
