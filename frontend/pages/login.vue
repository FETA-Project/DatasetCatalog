<template>
  <div class="flex flex-column gap-3 container">
    <Toast position="bottom-right" />
    <TabView id="login-register">
        <TabPanel header="Login">
            <div class="flex flex-column gap-3">
                <InputText
                  id="email"
                  autocomplete="email"
                  v-model="email"
                  placeholder="Email"
                  type="text"
                />
                <small v-if="email_error" class="p-error">
                    <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
                    Email is required.
                </small>
                <InputText
                  id="password"
                  autocomplete="current-password"
                  v-model="password"
                  placeholder="password"
                  type="password"
                />
                <small v-if="password_error" class="p-error">
                    <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
                    Password is required.
                </small>
                <Button
                  label="Login"
                  @click="login"
                />
            </div>
        </TabPanel>
        <TabPanel header="Register">
            <div class="flex flex-column gap-3">
            <InputText
              id="register-email"
              autocomplete="email"
              v-model="register_email"
              placeholder="Email"
              type="text"
              @blur="register_email_error = register_email.length === 0"
            />
            <small v-if="register_email_error" class="p-error">
                <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
                Email is required.
            </small>
            <InputText
              id="register-name"
              autocomplete="name"
              v-model="register_name"
              placeholder="Name"
              type="text"
              @blur="register_name_error = register_name.length === 0"
            />
            <small v-if="register_name_error" class="p-error">
                <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
                Name is required.
            </small>
            <InputText
              id="register-surname"
              autocomplete="surname"
              v-model="register_surname"
              placeholder="Surname"
              type="text"
              @blur="register_surname_error = register_surname.length === 0"
            />
            <small v-if="register_surname_error" class="p-error">
                <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
                Surname is required.
            </small>
            <InputText
              id="register-password"
              autocomplete="password"
              v-model="register_password"
              placeholder="Password"
              type="password"
              @blur="register_password_error = register_password.length === 0"
            />
            <small v-if="register_password_error" class="p-error">
                <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
                Password is required.
            </small>
            <InputText
              id="repeat-password"
              v-model="repeat_password"
              placeholder="Repeat Password"
              type="password"
              @blur="repeat_password_error = repeat_password.length === 0 || repeat_password !== register_password"
            />
            <small v-if="repeat_password_error" class="p-error">
                <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
                Repeat password is required and both passwords must match.
            </small>
            <Button
              label="Register"
              @click="register"
            />
            </div>
        </TabPanel>
    </TabView>
  </div>
</template>

<script setup>
import axios from "axios";
import { useToast } from "primevue/usetoast";

const toast = useToast();

const email = ref("")
const email_error = ref(false)
const password = ref("")
const password_error = ref(false)

const login_form_valid = () => {
    if (email.value == "") {
        email_error.value = true
        return false
    }

    if (password.value == "") {
        password_error.value = true
        return false
    }

    return true
}

const login = () => {
  const formData = new FormData();
  formData.append('email', email.value)
  formData.append('password', password.value)

  console.log('login')
  console.log(formData)

  if (!login_form_valid()) {
      return
  }

  axios.post('/auth/login', formData)
    .then(response => {
        navigateTo('/')
    })
    .catch(error => {
        toast.add({
          severity: 'error',
          summary: 'Login Failed',
          detail: 'There was an error logging in',
          life: 3000
        })
    })
}

const register_email = ref("")
const register_email_error = ref(false)
const register_name = ref("")
const register_name_error = ref(false)
const register_surname = ref("")
const register_surname_error = ref(false)
const register_password = ref("")
const register_password_error = ref(false)
const repeat_password = ref("")
const repeat_password_error = ref(false)

const register_form_valid = () => {

    if (register_email.value == "") {
        register_email_error.value = true
        return false
    }

    if (register_name.value == "") {
        register_name_error.value = true
        return false
    }

    if (register_surname.value == "") {
        register_surname_error.value = true
        return false
    }

    if (register_password.value == "") {
        register_password_error.value = true
        return false
    }

    if (repeat_password.value == "") {
        repeat_password_error.value = true
        return false
    }

    return true
}
const register = () => {
    const formData = new FormData();
    formData.append('email', register_email.value)
    formData.append('name', register_name.value)
    formData.append('surname', register_surname.value)
    formData.append('password', register_password.value)

    if (!register_form_valid()) {
        console.log("Form is not valid")
        return
    }

    axios.post('/auth/register', formData)
        .then(response => {
            console.log(response.data)
            toast.add({
                severity: 'success',
                summary: 'Register Success',
                detail: 'Registration successful',
                life: 3000
            })
        })
        .catch(error => {
            toast.add({
                severity: 'error',
                summary: 'Register Failed',
                detail: error.response.data,
                life: 3000
            })
        })
}

watch(register_email, (value) => {
    register_email_error.value = value.length === 0
})

watch(register_name, (value) => {
    register_name_error.value = value.length === 0
})

watch(register_surname, (value) => {
    register_surname_error.value = value.length === 0
})

watch(register_password, (value) => {
    register_password_error.value = value.length === 0
})

watch(repeat_password, (value) => {
    repeat_password_error.value = value.length === 0 || value !== register_password
})

</script>

<style scoped>

.container {
    width: 20em;
    margin: auto;
}
.error {
  color: red;
}

.error > * {
  border-color: red;
}

label {
  font-weight: bold;
}
</style>
