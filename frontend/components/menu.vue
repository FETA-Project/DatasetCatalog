<template>
    <div class="card relative z-2">
        <Menubar :model="items">
            <template #end>
                <div v-if="logged_in()">
                    <Button
                        text plain
                        :label="user.email"
                        @click=""
                    />
                    <Button
                        text plain
                        severity="danger"
                        label="Logout"
                        @click="logout()"
                    />
                </div>
                <div v-else>
                    <Button
                        text plain
                        label="Login"
                        @click="login()"
                    />
                </div>
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
        window.localStorage.setItem('user', user)
    })
})

const logged_in = () => user.value !== null
const is_admin = () => user.value.is_admin

const items = ref([
    {label: 'Catalog', icon: 'pi pi-fw pi-home', to: '/'},
    // {label: 'Requests', icon: 'pi pi-fw pi-ticket', to: '/requests'},
    {label: 'Users', icon: 'pi pi-fw pi-users', to: '/users', visible: () => logged_in() && is_admin()},
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

</script>

<style scoped>
/* Custom CSS to right-align the end slot */
.p-menubar .p-menubar-end {
  justify-content: flex-end;
}
</style>