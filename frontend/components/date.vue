<template>
    <span>{{ formatDate(props.timedate) }}</span>
</template>

<script>
    // import { defineProps } from 'vue'

    // const props = defineProps({
    //     timedate: {
    //         type: String,
    //         required: true,
    //     }
    // })

    function formatDate(timedate) {
        const date = new Date(timedate);
        
        // Get year, month, and day part from the date
        const year = date.toLocaleString("default", { year: "numeric" });
        const month = date.toLocaleString("default", { month: "2-digit" });
        const day = date.toLocaleString("default", { day: "2-digit" });
        
        return `${year}/${month}/${day}`;
    }
</script>