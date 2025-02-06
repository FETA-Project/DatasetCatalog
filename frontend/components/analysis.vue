<template>
    <template v-for="(field_value, field_key) in analysis">
        <Fieldset v-if="typeof field_value == 'object'" :legend="field_key.replaceAll('_', ' ')" :toggleable="true" style="margin-bottom: 1em">
            <ul style="list-style: none;" class="flex flex-column gap-1">
                <template v-for="(value, key) in field_value">
                    <li v-if="!key.endsWith('_info')">
                        <!-- <em v-if="typeof value != 'object'">({{ field_value[key+"_info"] }}) </em> -->
                        <b v-if="typeof value != 'object'">
                            <i v-if="field_value[key+'_info']" class="pi pi-info-circle" v-tooltip.left="field_value[key+'_info']"/>
                                {{ key.replaceAll("_", " ") }}: 
                        </b> 

                        <a v-if="typeof value =='string' && value.endsWith('.ipynb')" :href="jupyterURL(acronym, aliases, value)" target="_blank">{{ value }}</a>
                        <table v-else-if="check_if_json(value)" class="styled-table">
                            <tbody>
                                <tr v-for="(field, header) in JSON.parse(value)">
                                    <td>{{ header }}</td>
                                    <td>{{ field }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <span v-else-if="typeof value != 'object'" style="white-space: pre">
                            <span v-if="files.includes(value)" class="file-link" @click="downloadAnalysisFile(acronym, aliases, value)">{{ value }}</span>
                            <span v-else>{{ value }}</span>
                        </span>
                    </li>
                </template>
                <span v-if="typeof field_value == 'object'">
                      <Analysis :analysis="field_value" :acronym="acronym" :aliases="aliases" :files="files"/>
                </span>
            </ul>
        </Fieldset>
    </template>
</template>

<script setup>
import { defineProps } from 'vue'
import axios from 'axios';
import { useToast } from 'primevue/usetoast';

const toast = useToast()

const props = defineProps({
  acronym: {
    type: String,
    required: true
  },

  aliases: {
    type: Array,
    required: true
  },

  analysis: {
    type: Object,
    required: true
  },

  files: {
    type: Array,
    required: true
  }
});

const jupyterURL = (acronym, aliases, path) => {
    console.log(aliases)
    return "/jupyter/notebooks/" + acronym + (aliases.length == 0 ? '' : '.') + aliases.join(".") + "/" + path 
}

const downloadAnalysisFile = (acronym, aliases, filename) => {
    // axios.get(`/api/datasets/${encodeURIComponent(acronym)}/file`)
    axios.get(`/api/analysis_files/${encodeURIComponent(acronym)}/${encodeURIComponent(aliases)}/${encodeURIComponent(filename)}`)
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


const check_if_json = (string) => {

    // if (typeof string == "object") {
        // return false
    // }

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


</script>

<style>
.file-link {
  cursor: pointer;
  color: green;
  text-decoration: underline;
}
</style>