<script setup lang="ts">
interface Props {
  padding?: boolean
  hover?: boolean
}

withDefaults(defineProps<Props>(), {
  padding: true,
  hover: false
})
</script>

<template>
  <div
    :class="[
      'bg-card rounded-2xl border border-line shadow-sm transition-all duration-200',
      { 'p-6': padding },
      { 'hover:border-primary/40 hover:shadow-md cursor-pointer': hover }
    ]"
  >
    <slot />
  </div>
</template>
