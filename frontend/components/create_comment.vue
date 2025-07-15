<template>
  <div id="container" class="card flex justify-center">
    <div class="flex flex-col gap-4 container">
      <Toast position="bottom-right" />
      <!-- <div v-if="!edit" id="author" :class="{ error: authorError }" class="flex flex-col gap-2">
        <label for="author">
            <i class="pi pi-info-circle" v-tooltip.right="'Name of the commentor.'" />
            Name
        </label>
        <InputText
          id="author"
          v-model="author"
          aria-describedby="author-help"
          placeholder="Name"
        />
        <small v-if="authorError" class="p-error">
          <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
          Name is required.
        </small>
      </div> -->
      <div id="text" class="flex flex-col gap-2">
        <label for="Text">
          <i
            class="pi pi-info-circle"
            v-tooltip.right="'Text of the comment.'"
          />
          Text
        </label>
        <TextArea
          id="text"
          v-model="text"
          aria-describedby="text-help"
          placeholder="Text..."
          rows="5"
          cols="30"
          v-tooltip.bottom="'The text of the comment.'"
          required
        />
        <small v-if="textError" class="p-error">
          <i class="pi pi-exclamation-circle" style="font-size: 0.8rem" />
          Text is required.
        </small>
      </div>
      <Button
        :label="edit ? 'Edit Comment' : 'Add Comment'"
        @click="createComment"
      />
      <footer><small>* required field</small></footer>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";
import axios from "axios";

const router = useRouter();

const toast = useToast();

const dialogRef = inject("dialogRef");

const text = ref("");
const textError = ref(false);
// const author = ref("");
// const authorError = ref(false);
const belongs_to = ref("");
const edit = ref(false);
const comment_id = ref("");

onMounted(() => {
  belongs_to.value = dialogRef.value.data.belongs_to;
  edit.value = dialogRef.value.data.edit;
  text.value = dialogRef.value.data.text;
  comment_id.value = dialogRef.value.data.comment_id;
});

async function createComment() {
  const formData = new FormData();
  formData.append("text", text.value);
  if (text.value.length == 0) {
    textError.value = true;
    toast.add({
      severity: "error",
      summary: "Request Error",
      detail: "Text is required.",
      life: 3000,
    });
    return;
  }

  if (!edit.value) {
    //   formData.append("author", author.value)
    formData.append("belongs_to", belongs_to.value);
    //   if (author.value.length == 0) {
    //     authorError.value = true
    //     toast.add({
    //       severity: "error",
    //       summary: "Request Error",
    //       detail: 'Name is required.',
    //       life: 3000,
    //     });
    //     return
    //   }
    if (comment_id.value != null) {
      formData.append("parent_id", comment_id.value);
    }
  }

  await axios
    .post(
      `/api/comments${edit.value ? `/${comment_id.value}` : ""}`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data", // Make sure to set the correct content type
        },
      }
    )
    .then((response) => {
      toast.add({
        severity: "success",
        summary: edit ? "Comment Edited" : "Comment Added",
        life: 1000,
      });
      dialogRef.value.close(belongs_to.value);
    })
    .catch((error) => {
      console.log(error);
      toast.add({
        severity: "error",
        summary: edit ? "Comment Edit Error" : "Comment Add Error",
        detail: error.response.data.detail,
        life: 3000,
      });
    });
}

// watch(author, (value) => {
//     if(!edit.value){
//       authorError.value = value.length === 0
//     }
// })

watch(text, (value) => {
  textError.value = value.length === 0;
});
</script>

<style scoped>
.container {
  width: 30em;
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
