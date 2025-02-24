<template>
    <div class="card relative z-20">
        <Menubar :model="items">
            <template #end>
                    <!-- <Button
                        text plain
                        label="Login"
                        @click="login()"
                    /> -->
                    <Button
                        text plain
                        severity="danger"
                        label="Logout"
                        @click="logout_shib()"
                    />
                    <Button v-if="user"
                        text plain
                        label="local logout"
                        @click="logout()"
                    />
            </template>
        </Menubar>
        <DynamicDialog />
    </div>
</template>


<script setup>
import axios from 'axios'
import { useDialog } from 'primevue/usedialog'

const user = ref(null)

onMounted(() => {
    axios.get('/api/users/me').then(response => {
        console.log(response.data)
        user.value = response.data
    }).catch()
})

// FIXME: get user from shibboleth
// const logged_in = () => user.value !== null
// const is_admin = () => user.value.is_admin
const logged_in = () => true
const is_admin = () => true

const items = ref([
    {icon: 'pi pi-fw pi-sun', command: () => toggleDarkMode()},
    // {icon: 'pi pi-fw pi-moon', command: () => toggleDarkMode()},
    {label: 'Catalog', icon: 'pi pi-fw pi-home', command: () => navigateTo('/')},
    // {label: 'Requests', icon: 'pi pi-fw pi-ticket', to: '/requests'},
    logged_in() && is_admin() ? {label: 'Users', icon: 'pi pi-fw pi-users', command: () => navigateTo('/users')} : null,
    {label: 'Collection Tools', icon: 'pi pi-fw pi-search', command: () => navigateTo('/collection_tools')},
])

const dialog = useDialog()
const LoginDialog = defineAsyncComponent(() => import('../components/login.vue'))

const darkModeIcon = ref('pi pi-fw pi-sun')

onMounted(() => {
    if (localStorage.getItem('darkMode') === 'true') {
        document.documentElement.classList.add('dark');
        darkModeIcon.value = 'pi pi-fw pi-moon';
    }
})

function getDarkMode() {
    return document.documentElement.classList.contains('dark');
}

function toggleDarkMode() {
    document.documentElement.classList.toggle('dark');

    if (document.documentElement.classList.contains('dark')) {
        localStorage.setItem('darkMode', 'true');
        darkModeIcon.value = 'pi pi-fw pi-moon';
    } else {
        localStorage.removeItem('darkMode');
        darkModeIcon.value = 'pi pi-fw pi-sun';
    }
}

const login = () => {
    const dialogRef = dialog.open(LoginDialog, {
        props: {
            header: 'Login',
            modal: true,
            // title: title,
        },
    })
}

const logout = () => {
  axios.get('/auth/logout').then(response => {
    console.log(response)
    localStorage.removeItem('user')
    location.replace('/')
  })
}

const logout_shib = () => {
    document.cookie = 'authToken=; Max-Age=0; Path=/;';

    // Redirect to the backend endpoint for Shibboleth logout
    window.location.href = '/Shibboleth.sso/Logout?return=/Shibboleth.sso/Login';
}

</script>

<style scoped>
/* Custom CSS to right-align the end slot */
.p-menubar .p-menubar-end {
  justify-content: flex-end;
}
</style>