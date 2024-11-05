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
            <Button v-if="dataset.filename" @click="downloadDataset(dataset.acronym, dataset.acronym_aliases)" label="Download" icon="pi pi-download" severity="success" />
            <Button v-if="dataset.url" @click="getURL(dataset.url, true)" label="Open URL" icon="pi pi-link" severity="success" />
            <Button @click="editDataset(dataset.acronym, dataset.acronym_aliases)" label="Edit Info" icon="pi pi-pencil" />
            <Button @click="editAnalysis(dataset.acronym)" label="Edit Analysis" icon="pi pi-external-link" severity="secondary" />
        </h2>
        <Fieldset legend="Related Datasets" :toggleable="true" collapsed>
            <ul class="flex flex-column gap-2">
                <div v-if="origin_datasets.length > 0">
                    <b>Origin Datasets</b>
                    <li v-for="dataset in origin_datasets">
                        <span class="detail-link" @click="showDetail(dataset.acronym, dataset.aliases)">{{ dataset.acronym+'['+dataset.aliases+']'}}</span>
                    </li>
                </div>
                <div v-if="related_datasets.length > 0">
                    <b>Related Datasets</b>
                    <li v-for="dataset in related_datasets">
                        <span class="detail-link" @click="showDetail(dataset.acronym, dataset.aliases)">{{ dataset.acronym+'['+dataset.aliases+']'}}</span>
                    </li>
                </div>
                <div v-if="same_origin_datasets.length > 0">
                    <b>Datasets With the Same Origin</b>
                    <li v-for="dataset in same_origin_datasets">
                        <span class="detail-link" @click="showDetail(dataset.acronym, dataset.aliases)">{{ dataset.acronym+'['+dataset.aliases+']'}}</span>
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
                <li><b>Date Submitted: </b> <FormatedDate :datetime="dataset.date_submitted"/></li>
                <li>
                    <b>Submitter: </b>
                    <ul>
                        <li><b>Name: </b> {{ dataset.submitter.name }}</li>
                        <li><b>Email: </b> {{ dataset.submitter.email}}</li>
                    </ul>
                </li>
                <li> <b>Description: </b> {{ dataset.description }} </li>
                <li> <b>Format: </b> {{ dataset.format }} </li>
                <li> <b>DOI: </b> <a :href="dataset.doi" target="_blank">{{ dataset.doi }}</a></li>
                <li> <b>Origins DOI: </b> <a :href="dataset.origins_doi" target="_blank">{{ dataset.origins_doi }}</a></li>
                <li class="flex gap-2"> <b>Tags: </b> 
                    <!-- <div class="flex gap-2"><Chip v-for="tag in dataset.tags">{{ tag }}</Chip></div> -->
                    <Chip v-for="tag in dataset.tags">{{ tag }}</Chip>
                </li>
                <li> <b>Data URL: </b> <a :href="getURL(dataset.url)" about="_blank">{{ dataset.url }}</a></li>
                <li> <b>Data File: </b> {{ dataset.filename }} </li>
            </ul>
        </Fieldset>
        <Fieldset legend="Discussion" :toggleable="true" collapsed>
            <Button label="Add Comment" icon="pi pi-plus" severity="secondary" @click="createComment(dataset.acronym)" style="margin-bottom: 0.3em" />
            <Comments @signal="handleSignal" :comments="comments" :key="commentsKey"/>
        </Fieldset>
        <Analysis :analysis="analysis.analysis" :acronym="dataset.acronym"/>
    </div>
</template>

<script setup>
import axios from 'axios'
import MainMenu from '@/components/menu.vue'
import { useToast } from 'primevue/usetoast'
import { useDialog } from 'primevue/usedialog'
import Chip from 'primevue/chip';
import FormatedDate from '@/components/date.vue'
import Comments from '@/components/comments.vue'
import Analysis from '@/components/analysis.vue'

const toast = useToast()
const dataset_acronym = ref("Unknown")
const dataset_aliases = ref("Unknown")
const dataset = ref()
const related_datasets = ref()
const origin_datasets = ref()
const same_origin_datasets = ref()
const analysis = ref()
const edit_analysis_url = ref()
const route = useRoute()
const comments = ref({})
const commentsKey = ref(0)

const user = ref(null);

const dialog = useDialog()

const CreateCommentDialog = defineAsyncComponent(() => import('@/components/create_comment.vue'))

const showDetail = (acronym, aliases) => {
    navigateTo(`/detail/${encodeURIComponent(acronym)}/${encodeURIComponent(aliases)}`)
}

const handleSignal = (payload) => {
    refreshComments()
}

const refreshComments = () => {
    axios.get(`/api/comments/${encodeURIComponent(dataset_acronym.value)}`)
    .then(response => {
        comments.value = response.data
        commentsKey.value++
    })
    .catch(error => {
        toast.add({
            severity: 'error',
            summary: 'Error while getting comments',
            detail: error.response.data,
            life: 3000
        })
    })
}
const createComment = (belongs_to) => {
    const dialogRef = dialog.open(CreateCommentDialog, {
        props: {
            header: "Add Comment",
        },
        data: {
            belongs_to: belongs_to,
            parent_id: null,
            edit: false,
            text: "",
            comment_id: null,
        },
        onClose: () => {
            refreshComments()
        }
    })
    
}

const get_dataset = (acronym, aliases) => {
    console.log("get")
    console.log(acronym)
    console.log(aliases)
    axios.all([
        axios.get(`/api/datasets/${encodeURIComponent(acronym)}/${encodeURIComponent(aliases)}`),
        // axios.get(`/api/comments/${encodeURIComponent(acronym)}/${encodeURIComponent(aliases)}`),
        axios.get(`/api/comments/${encodeURIComponent(acronym)}`),
    ])
      .then(axios.spread((response_dataset, response_comments) => {
        //   dataset.value.analysis = {}
          dataset.value = response_dataset.data.dataset
          dataset.value.authors = dataset.value.authors.filter(author => author !== "")
          dataset.value.acronym_aliases = dataset.value.acronym_aliases.filter(alias => alias !== "")
          dataset.value.tags = dataset.value.tags.filter(tag => tag !== "")
          analysis.value = response_dataset.data.dataset.analysis
          edit_analysis_url.value = response_dataset.data.edit_analysis_url
          related_datasets.value = response_dataset.data.related_datasets
          origin_datasets.value = response_dataset.data.origin_datasets
          same_origin_datasets.value = response_dataset.data.same_origin_datasets
          comments.value = response_comments.data
          console.log(analysis.value)
      }))
      .catch(error => {
            toast.add({
                severity: 'error',
                summary: 'Error while getting dataset',
                detail: error.response.data,
                life: 3000
            })
      })
}

const editDataset = (acronym, aliases) => {
    if (aliases == "") {
        aliases = acronym
    }
    navigateTo(`/edit/${encodeURIComponent(acronym)}/${encodeURIComponent(aliases)}`)
}

// const editAnalysis = (acronym) => {
const editAnalysis = () => {
    window.open(edit_analysis_url.value, "_blank")
}

const getURL = (url, open = false) => {
    let _url = url
    if(url) {
        if (!/^https?:\/\//i.test(url)) {
            _url = `https://${url}`, "_blank";
        }

        return open ? window.open(_url, "_blank") : _url;
    } else {
        console.log("No URL - trying local file")
    }
}

const downloadDataset = (acronym, aliases) => {
    // axios.get(`/api/datasets/${encodeURIComponent(acronym)}/file`)
    axios.get(`/api/files/${encodeURIComponent(acronym)}/${encodeURIComponent(aliases)}`)
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
    dataset_aliases.value = decodeURIComponent(route.params.aliases)
    if (dataset_aliases.value == dataset_acronym.value) {
        dataset_aliases.value = ""
    }
    get_dataset(dataset_acronym.value, dataset_aliases.value)
    axios.get('/api/users/me')
        .then(response => {
            console.log(response.data)
            user.value = response.data
        })
        .catch()
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