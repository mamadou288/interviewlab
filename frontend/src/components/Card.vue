<template>
  <div :class="['bg-white rounded-lg shadow-md p-6', hoverable ? 'hover:shadow-lg transition-shadow cursor-pointer' : '']">
    <slot />
  </div>
</template>

<script setup>
defineProps({
  hoverable: {
    type: Boolean,
    default: false
  }
})
</script>

