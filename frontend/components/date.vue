<template>
    <span>{{ formatDate(props.date) }}</span>
</template>

<script>
    import { defineProps } from 'vue'

    const props = defineProps({
        date: {
            type: String,
            required: true,
        }
    })

    function formatDate(timedate) {
        const _date = new Date(timedate);
        
        // Get year, month, and day part from the date
        const year = _date.toLocaleString("default", { year: "numeric" });
        const month = _date.toLocaleString("default", { month: "2-digit" });
        const day = _date.toLocaleString("default", { day: "2-digit" });
        
        return `${year}/${month}/${day}`;
    }
</script>