<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h3 class="text-lg font-semibold text-gray-700 mb-2">{{ title }}</h3>
    <p :class="['text-3xl font-bold', colorClass]">{{ value }}</p>
    <p v-if="subtitle" class="text-sm text-gray-500 mt-1">{{ subtitle }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  subtitle: {
    type: String,
    default: null
  },
  colorClass: {
    type: String,
    default: 'text-blue-600'
  }
})
</script>

