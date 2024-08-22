<template>
    <div class="flex flex-column gap-3">
        <Toast position="bottom-right" />
        <MainMenu />
        <h1>
            Details of {{ dataset_acronym }}
            <div v-if="dataset.status == 'requested'">
                <Badge value="Requested" severity="info"/>
                <br />
            </div>
        </h1>

        <h2 class="flex gap-2">
            <Button @click="downloadDataset(dataset.acronym)" label="Download" icon="pi pi-download" severity="success" />
            <Button @click="editDataset(dataset.acronym)" label="Edit Info" icon="pi pi-pencil" />
            <Button @click="editAnalysis(dataset.acronym)" label="Edit Analysis" icon="pi pi-external-link" severity="secondary" />
        </h2>
        <Fieldset legend="Related Datasets" :toggleable="true" collapsed>
            <ul class="flex flex-column gap-2">
                <div v-if="origin_datasets.length > 0">
                    <b>Origin Datasets</b>
                    <li v-for="acronym in origin_datasets">
                        <span class="detail-link" @click="showDetail(acronym)">{{ acronym }}</span>
                    </li>
                </div>
                <div v-if="related_datasets.length > 0">
                    <b>Related Datasets</b>
                    <li v-for="acronym in related_datasets">
                        <span class="detail-link" @click="showDetail(acronym)">{{ acronym }}</span>
                    </li>
                </div>
                <div v-if="same_origin_datasets.length > 0">
                    <b>Datasets With the Same Origin</b>
                    <li v-for="acronym in same_origin_datasets">
                        <span class="detail-link" @click="showDetail(acronym)">{{ acronym }}</span>
                    </li>
                </div>
            </ul>
        </Fieldset>
        <Fieldset legend="Details" :toggleable="true">
            <ul style="list-style: none" class="flex flex-column gap-2">
                <li class="flex gap-2"> <b>Acronym Aliases: </b> 
                    <Chip v-for="acronym_alias in dataset.acronym_aliases">{{ acronym_alias }}</Chip>
                </li>
                <li><b>Dataset Title: </b> {{ dataset.title }}</li>
                <li><b>Paper Title: </b> {{ dataset.paper_title }}</li>
                <li class="flex gap-2"> <b>Authors: </b> 
                    <Chip v-for="author in dataset.authors">{{ author }}</Chip>
                </li>
                <li><b>Date Submitted: </b> {{ dataset.date_submitted }}</li>
                <li>
                    <b>Submitter: </b>
                    <ul>
                        <li><b>Name: </b> {{ dataset.submitter.name }}</li>
                        <li><b>Email: </b> {{ dataset.submitter.email}}</li>
                    </ul>
                </li>
                <li> <b>Description: </b> {{ dataset.description }} </li>
                <li> <b>DOI: </b> <a :href="dataset.doi" target="_blank">{{ dataset.doi }}</a></li>
                <li> <b>Origins DOI: </b> <a :href="dataset.origins_doi" target="_blank">{{ dataset.origins_doi }}</a></li>
                <li class="flex gap-2"> <b>Tags: </b> 
                    <!-- <div class="flex gap-2"><Chip v-for="tag in dataset.tags">{{ tag }}</Chip></div> -->
                    <Chip v-for="tag in dataset.tags">{{ tag }}</Chip>
                </li>
                <li> <b>Data URL: </b> <a :href="dataset.url" target="_blank">{{ dataset.url }}</a></li>
            </ul>
        </Fieldset>
        <!-- <Fieldset legend="Base Info" :toggleable="true">
            <ul style="list-style: none">
                <template v-for="(value, key) in dataset.analysis">
                    <li v-if="!(typeof value == 'object')">
                        <b>{{ key }}: </b> 
                        <a v-if="typeof value == 'string' && value.endsWith('.ipynb')" :href="jupyterURL(value)" target="_blank">{{ value }}</a>
                        <span v-else>{{ value }} - {{ check_if_json(value) }}</span>
                    </li>
                </template>
            </ul>
        </Fieldset> -->
        <template v-for="(field_value, field_key) in analysis.analysis">
            <Fieldset v-if="typeof field_value == 'object'" :legend="field_key.replaceAll('_', ' ')" :toggleable="true">
                <ul style="list-style: none;" class="flex flex-column gap-1">
                    <li v-for="(value, key) in field_value">
                        <b>{{ key.replaceAll("_", " ") }}: </b> 

                        <a v-if="typeof value =='string' && value.endsWith('.ipynb')" :href="jupyterURL(dataset.acronym + '/' + value)" target="_blank">{{ value }}</a>
                        <table v-else-if="check_if_json(value)" class="styled-table">
                            <tbody>
                                <tr v-for="(field, header) in JSON.parse(value)">
                                    <td>{{ header }}</td>
                                    <td>{{ field }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <!-- <span v-else-if="typeof value == 'string'" style="white-space: pre">{{ value }}</span> -->
                        <!-- <pre v-else-if="check_if_json(value)">{{ JSON.stringify(JSON.parse(value), null, 2) }}</pre> -->
                        <span v-else style="white-space: pre">{{ value }}</span>
                    </li>
                </ul>
            </Fieldset>
        </template>
    </div>
</template>

<script setup>
import axios from 'axios'
import MainMenu from '@/components/menu.vue'
import { useToast } from 'primevue/usetoast'
import Chip from 'primevue/chip';
import FormatedDate from '@/components/date.vue'
const toast = useToast()
const dataset_acronym = ref("Unknown")
const dataset = ref()
const related_datasets = ref()
const origin_datasets = ref()
const same_origin_datasets = ref()
const analysis = ref()
const edit_analysis_url = ref()
const route = useRoute()

const openRepo = (repo) => {window.open("https://doi.org/" + repo, "_blank")}

const jupyterURL = (path) => {return "/jupyter/notebooks/" + path}

const check_if_json = (string) => {

    if (typeof string != "string") {
        return false
    }

    if (!string.includes("{") || !string.includes("}")) {
        return false
    }

    try {
        JSON.parse(string)
        return true
    } catch (e) {
        return false
    }
}

const showDetail = (acronym) => {
    navigateTo(`/detail/${encodeURIComponent(acronym)}`)
}

const get_dataset = (acronym) => {
    axios.get(`/api/datasets/${encodeURIComponent(acronym)}`)
      .then(response => {
        //   dataset.value.analysis = {}
          console.log(response.data)
          dataset.value = response.data.dataset
          dataset.value.authors = dataset.value.authors.filter(author => author !== "")
          dataset.value.tags = dataset.value.tags.filter(tag => tag !== "")
          analysis.value = response.data.analysis
          edit_analysis_url.value = response.data.edit_analysis_url
          related_datasets.value = response.data.related_datasets
          origin_datasets.value = response.data.origin_datasets
          same_origin_datasets.value = response.data.same_origin_datasets
          console.log(dataset.value)
          console.log(related_datasets.value)
          console.log(origin_datasets.value)
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

const editDataset = (acronym) => {
    navigateTo(`/edit/${encodeURIComponent(acronym)}`)
}

// const editAnalysis = (acronym) => {
const editAnalysis = () => {
    console.log(edit_analysis_url.value)
    window.open(edit_analysis_url.value, "_blank")
    // toast.add({
    //     severity: 'info',
    //     summary: 'Edit Analysis',
    //     detail: `To edit analysis of [${acronym}] you need to go to [${analysis.value.path}] on local machine and edit [analysis.toml]`,
    //     // life: 3000
    //     })
}

const downloadDataset = (acronym) => {
    if(dataset.value.url) {
        window.open(dataset.value.url, "_blank")
        return
    } else {
        console.log("No URL - trying local file")
    }
    // axios.get(`/api/datasets/${encodeURIComponent(acronym)}/file`)
    axios.get(`/api/files/${encodeURIComponent(acronym)}`)
        .then(response => {
            const blob = new Blob([response.data], { type: response.headers['content-type'] });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            let filename = "filename"
            const matches = response.headers['content-disposition'].match(/filename="(.+)"/);
            if (matches && matches[1]) {
               filename = matches[1];
            }
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
        })
        .catch(error => {
            toast.add({
                severity: 'error',
                summary: 'Error while downloading dataset',
                detail: error.response.data,
                life: 3000
            })
        })
}


onMounted(() => { 
    // dataset_title.value = "dataset_example_name"
    dataset_acronym.value = decodeURIComponent(route.params.acronym)
    get_dataset(dataset_acronym.value)
})
</script>

<style>
li > b {
    text-transform: capitalize;
}

fieldset > legend {
    text-transform: capitalize;
}

.container {
    width: 30em;
}

.info {
    border-bottom: 1px dotted #000;
    text-decoration: none;
}

.json-table {
    border: 1px solid black;
}

.json-table td {
    border: 1px solid black;
}

.styled-table {
    border-collapse: collapse;
    margin: 25px 0;
    font-size: 0.9em;
    font-family: sans-serif;
    min-width: 400px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
}

.styled-table thead tr {
    /* background-color: #009879; */
    color: #ffffff;
    text-align: left;
}

.styled-table th,
.styled-table td {
    padding: 12px 15px;
}

.styled-table tbody tr {
    border-bottom: 1px solid #dddddd;
}

.styled-table tbody tr:nth-of-type(even) {
    background-color: #f3f3f3;
}

/* .styled-table tbody tr:last-of-type {
    border-bottom: 2px solid #009879;
} */
/* .styled-table tbody tr.active-row {
    font-weight: bold;
    color: #009879;
} */



.p-toast-detail {
  white-space: normal; /* Ensures text wraps to the next line */
  word-break: break-word; /* Prevents long words from breaking the layout */
}

.detail-link {
  cursor: pointer;
  text-decoration: dotted underline;
}

</style>