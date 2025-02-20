<template>
    <div class="flex flex-col gap-4">
        <Toast position="bottom-right" />
        <MainMenu />
        <h1 class="m-4 text-3xl font-bold">
            Details of {{ 
                dataset.acronym
                + (dataset.versions.length == 0 ? '' : '.')
                + dataset.versions.join('.') 
                }}
            <br/>
            <Badge :value="'Analysis: ' + dataset.analysis_status" severity="info"/>
            <div v-if="dataset.status == 'requested'">
                <Badge value="Requested" severity="info"/>
                <br />
            </div>
        </h1>

        <h2 class="flex gap-2">
            <Button v-if="dataset.filename" @click="downloadDataset(dataset.acronym, dataset.versions)" label="Download" icon="pi pi-download" severity="success" />
            <Button v-if="dataset.url" @click="getURL(dataset.url, true)" label="Open URL" icon="pi pi-link" severity="success" />
            <Button @click="editDataset(dataset.acronym, dataset.versions)" label="Edit Info" icon="pi pi-pencil" />
            <Button @click="editAnalysis(dataset.acronym)" label="Edit Analysis" icon="pi pi-external-link" severity="secondary" />
        </h2>
        <Fieldset legend="Related Datasets" :toggleable="true" collapsed>
            <ul class="flex flex-col gap-2">
                <div v-if="version_parents.length > 0">
                    <b>Dataset's Parents</b>
                    <li v-for="dataset in version_parents">
                        <span class="detail-link" @click="showDetail(dataset.acronym, dataset.versions)">{{ dataset.acronym+'['+dataset.versions+']'}}</span>
                    </li>
                </div>
                <div v-if="version_children.length > 0">
                    <b>Dataset's Children</b>
                    <li v-for="dataset in version_children">
                        <span class="detail-link" @click="showDetail(dataset.acronym, dataset.versions)">{{ dataset.acronym+'['+dataset.versions+']'}}</span>
                    </li>
                </div>
            </ul>
        </Fieldset>
        <Fieldset legend="Details" :toggleable="true">
            <ul style="list-style: none" class="flex flex-col gap-2">
                <li class="flex gap-2"> <b>Versions: </b> 
                    <div class="flex gap-1" v-if="dataset.versions.length > 1 || dataset.versions[0] != ''">
                        <Chip v-for="version in dataset.versions">{{ version }}</Chip>
                    </div>
                </li>
                <li><b>Dataset Title: </b> {{ dataset.title }}</li>
                <li><b>Paper Title: </b> {{ dataset.paper_title }}</li>
                <li class="flex gap-2"> <b>Authors: </b> 
                    <div class="flex gap-1" v-if="dataset.authors.length > 1 || dataset.authors[0] != ''">
                        <Chip v-for="author in dataset.authors">{{ author }}</Chip>
                    </div>
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
                <li> <b>Label Name: </b> {{ dataset.label_name }} </li>
                <li class="flex gap-2"> <b>Tags: </b> 
                    <!-- <div class="flex gap-2"><Chip v-for="tag in dataset.tags">{{ tag }}</Chip></div> -->
                    <div class="flex gap-1" v-if="dataset.tags.length > 1 || dataset.tags[0] != ''">
                        <Chip v-for="tag in dataset.tags">{{ tag }}</Chip>
                    </div>
                </li>
                <li> <b>Data URL: </b> <a :href="getURL(dataset.url)" about="_blank">{{ dataset.url }}</a></li>
                <li> <b>Data File: </b> {{ dataset.filename }} </li>
            </ul>
        </Fieldset>
        <Fieldset legend="Discussion" :toggleable="true" collapsed>
            <Button label="Add Comment" icon="pi pi-plus" severity="secondary" @click="createComment(dataset.acronym)" style="margin-bottom: 0.3em" />
            <Comments @signal="handleSignal" :comments="comments" :key="commentsKey"/>
        </Fieldset>
        <Analysis :analysis="analysis.analysis" :acronym="dataset.acronym" :versions="dataset.versions" :files="dataset.files"/>
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
const dataset_versions = ref("Unknown")
const dataset = ref()
const version_parents = ref()
const version_children = ref()
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

const showDetail = (acronym, versions) => {
    if (versions == "") {
        versions = "*"
    }
    navigateTo(`/detail/${encodeURIComponent(acronym)}/${encodeURIComponent(versions)}`)
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
            modal: true,
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

const get_dataset = (acronym, versions) => {
    console.log("get")
    console.log(acronym)
    console.log(versions)
    axios.all([
        axios.get(`/api/datasets/${encodeURIComponent(acronym)}/${encodeURIComponent(versions)}`),
        // axios.get(`/api/comments/${encodeURIComponent(acronym)}/${encodeURIComponent(versions)}`),
        axios.get(`/api/comments/${encodeURIComponent(acronym)}`),
    ])
      .then(axios.spread((response_dataset, response_comments) => {
        //   dataset.value.analysis = {}
          dataset.value = response_dataset.data.dataset
          dataset.value.authors = dataset.value.authors.filter(author => author !== "")
          dataset.value.versions = dataset.value.versions.filter(version => version !== "")
          dataset.value.tags = dataset.value.tags.filter(tag => tag !== "")
          analysis.value = response_dataset.data.dataset.analysis
          edit_analysis_url.value = response_dataset.data.edit_analysis_url
          related_datasets.value = response_dataset.data.related_datasets
          origin_datasets.value = response_dataset.data.origin_datasets
          same_origin_datasets.value = response_dataset.data.same_origin_datasets
          version_children.value = response_dataset.data.version_children
          version_parents.value = response_dataset.data.version_parents
          comments.value = response_comments.data
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

const editDataset = (acronym, versions) => {
    if (versions == "") {
        versions = "*"
    }
    navigateTo(`/edit/${encodeURIComponent(acronym)}/${encodeURIComponent(versions)}`)
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

const downloadDataset = (acronym, versions) => {
    // axios.get(`/api/datasets/${encodeURIComponent(acronym)}/file`)
    axios.get(`/api/files/${encodeURIComponent(acronym)}/${encodeURIComponent(versions)}`)
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
    dataset_versions.value = decodeURIComponent(route.params.versions)
    get_dataset(dataset_acronym.value, dataset_versions.value)
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