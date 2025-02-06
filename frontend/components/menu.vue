<template>
    <div class="card relative z-2">
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
    {label: 'Catalog', icon: 'pi pi-fw pi-home', to: '/'},
    // {label: 'Requests', icon: 'pi pi-fw pi-ticket', to: '/requests'},
    {label: 'Users', icon: 'pi pi-fw pi-users', to: '/users', visible: () => logged_in() && is_admin()},
    {label: 'Collection Tools', icon: 'pi pi-fw pi-search', to: '/collection_tools'},
])

const dialog = useDialog()
const LoginDialog = defineAsyncComponent(() => import('../components/login.vue'))

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