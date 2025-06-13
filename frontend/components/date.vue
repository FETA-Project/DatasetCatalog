<template>
  <span> {{ format(datetime) }}</span>
</template>

<script setup>
import { defineProps } from "vue";

const props = defineProps({
  datetime: {
    type: String,
    required: true,
  },
});

const format = (timedate) => {
  const _date = new Date(timedate);

  // Get year, month, and day part from the date
  // console.log(_date)
  //   const year = _date.toLocaleString("default", { year: "numeric" });
  //   const month = _date.toLocaleString("default", { month: "2-digit" });
  //   const day = _date.toLocaleString("default", { day: "2-digit" });
  //   const hour = _date.toLocaleString("default", { hour: "2-digit" });
  //   const minute = _date.toLocaleString("default", { minute: "2-digit" });
  //   const second = _date.toLocaleString("default", { second: "2-digit" });

  //   // return `${_date.toLocaleDateString()} ${_date.toLocaleTimeString()}`
  //   return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
  try {
    return _date.toISOString().replace("T", " ").slice(0, -5);
  } catch (error) {
    return error;
  }
};
</script>
