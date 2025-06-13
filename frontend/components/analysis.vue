<template>
  <template v-for="(field_value, field_key) in analysis">
    <Fieldset
      v-if="typeof field_value == 'object'"
      :legend="field_key.replaceAll('_', ' ')"
      :toggleable="true"
      style="margin-bottom: 1em"
    >
      <ul style="list-style: none" class="flex flex-col gap-1">
        <template v-for="(value, key) in field_value">
          <li v-if="!key.endsWith('_info')">
            <!-- <em v-if="typeof value != 'object'">({{ field_value[key+"_info"] }}) </em> -->
            <b v-if="typeof value != 'object'">
              <i
                v-if="field_value[key + '_info']"
                class="pi pi-info-circle"
                v-tooltip.left="field_value[key + '_info']"
              />
              {{ key.replaceAll("_", " ") }}:
            </b>

            <a
              class="font-medium text-orange-500 dark:text-orange-600 hover:underline cursor-pointer"
              v-if="typeof value == 'string' && value.endsWith('.ipynb')"
              :href="nbviewerURL(acronym, versions, value)"
              target="_blank"
              >{{ value }}</a
            >
            <table v-else-if="check_if_json(value)" class="styled-table">
              <tbody>
                <tr v-for="(field, header) in Jsonic(value)">
                  <td class="p-4">{{ header }}</td>
                  <td class="p-4">{{ field }}</td>
                </tr>
              </tbody>
            </table>
            <span v-else-if="typeof value != 'object'" style="white-space: pre">
              <span
                v-if="files.includes(value)"
                class="font-medium text-green-500 dark:text-green-600 hover:underline cursor-pointer"
                @click="downloadAnalysisFile(acronym, versions, value)"
                >{{ value }}</span
              >
              <MDC v-else class="prose dark:prose-invert" :value="value" />
            </span>
          </li>
        </template>
        <span v-if="typeof field_value == 'object'">
          <Analysis
            :analysis="field_value"
            :acronym="acronym"
            :versions="versions"
            :files="files"
          />
        </span>
      </ul>
    </Fieldset>
  </template>
</template>

<script setup>
import { defineProps } from "vue";
import axios from "axios";
import { useToast } from "primevue/usetoast";
import { Jsonic } from "jsonic";

const toast = useToast();

const props = defineProps({
  acronym: {
    type: String,
    required: true,
  },

  versions: {
    type: Array,
    required: true,
  },

  analysis: {
    type: Object,
    required: true,
  },

  files: {
    type: Array,
    required: true,
  },
});

const nbviewerURL = (acronym, versions, path) => {
  console.log(versions);
  return (
    "/nbviewer/localfile/" +
    acronym +
    (versions.length == 0 ? "" : ".") +
    versions.join(".") +
    "/" +
    path
  );
};

const downloadAnalysisFile = (acronym, versions, filename) => {
  // axios.get(`/api/datasets/${encodeURIComponent(acronym)}/file`)
  axios
    .get(
      `/api/analysis_files/${encodeURIComponent(acronym)}/${encodeURIComponent(
        versions
      )}/${encodeURIComponent(filename)}`
    )
    .then((response) => {
      const blob = new Blob([response.data], {
        type: response.headers["content-type"],
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      let filename = "filename";
      const matches =
        response.headers["content-disposition"].match(/filename="(.+)"/);
      if (matches && matches[1]) {
        filename = matches[1];
      }
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
    })
    .catch((error) => {
      toast.add({
        severity: "error",
        summary: "Error while downloading dataset",
        detail: error.response.data,
        life: 3000,
      });
    });
};

const check_if_json = (string) => {
  if (typeof string != "string") {
    return false;
  }

  if (!string.includes("{") || !string.includes("}")) {
    return false;
  }

  try {
    Jsonic(string);
    return true;
  } catch (e) {
    return false;
  }
};
</script>

<style>
.file-link {
  cursor: pointer;
  color: green;
  text-decoration: underline;
}

.p-fieldset-legend-label {
  text-transform: capitalize;
}

.styled-table {
  width: fit-content;
  margin: 25px 0;
  max-width: 80%;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  max-height: 400px;
  overflow-y: auto;
  display: block;
}

.dark .styled-table {
  box-shadow: 0 0 20px rgba(100, 100, 100, 0.15);
}

.styled-table thead tr {
  /* background-color: #009879; */
  /* color: #ffffff; */
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

.dark .styled-table tbody tr:nth-of-type(even) {
  background-color: #f3f3f309;
}

.dark .styled-table tbody tr:nth-of-type(odd) {
  background-color: #f3f3f31b;
}
</style>
