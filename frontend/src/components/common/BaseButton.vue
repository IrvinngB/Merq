<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false
})
</script>

<template>
  <button
    :disabled="disabled || loading"
    :class="[
      'inline-flex items-center justify-center font-medium rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-bg cursor-pointer shadow-sm',
      {
        'bg-primary text-white hover:bg-primary-hover focus:ring-primary': variant === 'primary',
        'bg-card text-text hover:bg-bg-secondary focus:ring-line border border-line': variant === 'secondary',
        'bg-danger text-white hover:bg-danger/80 focus:ring-danger': variant === 'danger',
        'bg-transparent text-text-secondary hover:text-text hover:bg-card shadow-none': variant === 'ghost',
        'px-3 py-1.5 text-sm': size === 'sm',
        'px-5 py-2.5 text-sm': size === 'md',
        'px-6 py-3 text-base': size === 'lg',
        'opacity-50 cursor-not-allowed': disabled || loading
      }
    ]"
  >
    <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
    </svg>
    <slot />
  </button>
</template>
