<template>
    <div class="card flex flex-column gap-3">
        <MainMenu />
        <h1>{{ dataset.title }}</h1>

        <h2 class="flex gap-2">
            <Button label="Download" icon="pi pi-download" severity="success" />
            <Button @click="openRepo(dataset.doi)" label="Repository" icon="pi pi-external-link" severity="secondary" />
        </h2>
        <Fieldset legend="Details" :toggleable="true" :collapsed="true">
            <ul style="list-style: none">
                <li>
                    <b>Title: </b> {{ dataset.title }}
                </li>
                <li>
                    <b>Description: </b> {{ dataset.description }}
                </li>
                <li>
                    <b>DOI: </b> <a :href="'https://doi.org/' + dataset.doi" target="_blank">{{ dataset.doi }}</a>
                </li>
                <li>
                    <b>Origins DOI: </b>
                    <ul>
                        <li v-for="value in dataset.origins_doi">
                            <a :href="'https://doi.org/' + value" target="_blank">{{ value }}</a>
                        </li>
                    </ul>
                </li>
                <li>
                    <b>Date: </b> {{ dataset.date }}
                </li>
                <li>
                    <b>Requester </b>
                    <ul>
                        <li>
                            <b>Name: </b> {{ dataset.requester.name }}
                        </li>
                        <li>
                            <b>Email: </b> {{ dataset.requester.email }}
                        </li>
                    </ul>
                </li>
                <li>
                    <b>Tags: </b>
                    <span>{{ dataset.tags }}</span>
                </li>
            </ul>
        </Fieldset>

        <Fieldset legend="Report" :toggleable="true">
            <div class="flex flex-column gap-2">
                <ul style="list-style: none">
                    <li v-for="value, name in dataset.report">
                        <span v-if="(typeof value === 'object')">
                            <b>{{ name }}</b>: 
                            <ul>
                                <li v-for="value, name in value">
                                    <b>{{ name }}</b>: {{ value }}
                                </li>
                            </ul>
                        </span>
                        <span v-else>
                            <b>{{ name }}</b>: {{ value }}
                        </span>
                    </li>
                </ul>
                <!-- <Card>
                    <template #title>Redundancy</template>
                    <template #content>Content</template>
                </Card>
                <Card>
                    <template #title>Association</template>
                    <template #content>Content</template>
                </Card>
                <Card>
                    <template #title>Class Similiarity</template>
                    <template #content>Content</template>
                </Card> -->
            </div>
        </Fieldset>

        <Fieldset legend="Metadata" :toggleable="true" :collapsed="true" class="flex gap-2">
            <ScrollPanel style="width:100%; height: 500px">
                <pre>
                    {{ dataset.metadata }}
                </pre>
            </ScrollPanel>
        </Fieldset>

        <Fieldset legend="Related Datasets" :toggleable="true" :collapsed="true">
            ...
        </Fieldset>

    </div>
</template>

<script setup>
    import axios from 'axios'
    import MainMenu from '@/components/menu.vue'
    const route = useRoute()
    const title = decodeURIComponent(route.params.title)
    console.log(title)
    const dataset = ref()

    const get_dataset = (title) => {
        axios.get(`/api/datasets/${title}`)
          .then(response => {
              dataset.value = response.data
              dataset.value.tags = dataset.value.tags.join(', ')
          })
          .catch(error => {
                toast.add({
                    severity: 'error',
                    summary: 'Error while getting dataset',
                    detail: error.response.data,
                    life: 3000
                })
          })
    }

    const openRepo = (repo) => {window.open("https://doi.org/" + repo, "_blank")}

    onMounted(() => { get_dataset(title) })
</script>