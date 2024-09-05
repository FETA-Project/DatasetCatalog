<template>
    <Accordion :activeIndex="0" v-for="comment in comments" style="margin-top: 0.5rem; margin-bottom: 0.5rem">
        <AccordionTab :header="comment.deleted ? '&lt;deleted&gt;' : comment.author">
            <span v-if="comment.deleted">&lt;deleted&gt;</span>
            <span v-else>{{  comment.text }}</span>
            <hr/>
            <small class="flex justify-content-between flex-wrap">
                <div>
                    <FormatedDate :datetime="comment.date"/> <span v-if="comment.edited"> | edited </span>
                </div>
                <div v-if="!comment.deleted">
                     <span class="link" @click="createComment(comment)">Reply</span> | 
                     <span class="link" @click="createComment(comment, true)">Edit</span> | 
                     <span class="link" @click="deleteComment(comment)">Delete</span>
                </div>
            </small>
            <Comments @signal="refresh" :comments="comment.children" />
        </AccordionTab>
    </Accordion>
  </template>
  
<script setup>
  import { defineProps, defineEmits } from 'vue';
  import FormatedDate from '@/components/date.vue'
  import { useDialog } from 'primevue/usedialog';
  import { useToast } from 'primevue/usetoast';
  import axios from 'axios';

  const dialog = useDialog()
  const toast = useToast()
  const dialogRef = inject("dialogRef")
  const CreateCommentDialog = defineAsyncComponent(() => import('@/components/create_comment.vue'))

  const emit = defineEmits(['signal']);

  const props = defineProps({
    comments: {
      type: [Object, Array],
      required: true
    }
  });

const createComment = (comment, edit = false) => {
        console.log(comment)
        const dialogRef = dialog.open(CreateCommentDialog, {
        props: {
            header: edit ? "Edit Comment" : "Add Comment",
        },
        data: {
            belongs_to: comment.belongs_to,
            comment_id: comment.id,
            edit: edit,
            text: edit ? comment.text : "",
        },
        onClose: () => {
            refresh(comment.belongs_to)
       }
    })
  }

  const deleteComment = (comment) => {
    axios
      .delete("/api/comments/" + comment.id)
      .then(() => {
        toast.add({ severity: 'success', summary: 'Success', detail: 'Comment deleted', life: 3000 });
        refresh(comment.belongs_to)
      })
      .catch((error) => {
        toast.add({ severity: 'error', summary: 'Error', detail: error, life: 3000 });
      } )
    }
    const refresh = (acronym) => {
        emit('signal', acronym);
    }
  </script>

<style>
    .link {
        cursor: pointer;
    }
    .link:hover {
        text-decoration: underline;
    }
</style>
  