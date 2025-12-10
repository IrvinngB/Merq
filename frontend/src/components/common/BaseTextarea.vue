<script setup lang="ts">
interface Props {
  label?: string
  placeholder?: string
  error?: string
  required?: boolean
  rows?: number
}

withDefaults(defineProps<Props>(), {
  required: false,
  rows: 4
})

const model = defineModel<string>()
</script>

<template>
  <div class="space-y-2">
    <label v-if="label" class="block text-sm font-medium text-text">
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>
    <textarea
      v-model="model"
      :placeholder="placeholder"
      :required="required"
      :rows="rows"
      :class="[
        'block w-full rounded-xl border px-4 py-3 text-sm transition-all duration-200 resize-none',
        'bg-bg-secondary text-text placeholder-text-secondary',
        'focus:outline-none focus:ring-2 focus:ring-offset-0',
        error
          ? 'border-danger focus:border-danger focus:ring-danger/30'
          : 'border-line focus:border-primary focus:ring-primary/30'
      ]"
    />
    <p v-if="error" class="text-sm text-danger">{{ error }}</p>
  </div>
</template>
