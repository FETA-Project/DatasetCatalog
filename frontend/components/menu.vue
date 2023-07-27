<template>
    <Menubar :model="menu" />
</template>

<script setup>

const menu = ref([
    {label: 'Catalog', icon: 'pi pi-fw pi-home', to: '/'},
    {label: 'Requests', icon: 'pi pi-fw pi-ticket', to: '/requests'},
])


</script>