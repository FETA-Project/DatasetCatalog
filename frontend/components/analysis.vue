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

                        <a v-if="typeof value =='string' && value.endsWith('.ipynb')" :href="jupyterURL(acronym + '/' + value)" target="_blank">{{ value }}</a>
                        <table v-else-if="check_if_json(value)" class="styled-table">
                            <tbody>
                                <tr v-for="(field, header) in JSON.parse(value)">
                                    <td>{{ header }}</td>
                                    <td>{{ field }}</td>
                                </tr>
                            </tbody>
                        </table>
                        <span v-else-if="typeof value != 'object'" style="white-space: pre">{{ value }}</span>
                    </li>
                </template>
                <span v-if="typeof field_value == 'object'">
                      <Analysis :analysis="field_value" :acronym="acronym"/>
                </span>
            </ul>
        </Fieldset>
    </template>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  acronym: {
    type: String,
    required: true
  },

  analysis: {
    type: Object,
    required: true
  },
});

const jupyterURL = (path) => {return "/jupyter/notebooks/" + path}

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