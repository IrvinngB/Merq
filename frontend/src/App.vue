<script setup lang="ts">
import { onMounted } from 'vue'
import { TheNavbar, TheFooter } from '@/components/layout'
import { useAuthStore } from '@/stores'

const authStore = useAuthStore()

onMounted(() => {
  authStore.fetchCurrentUser()
})
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <TheNavbar />
    <main class="flex-1">
      <RouterView />
    </main>
    <TheFooter />
  </div>
</template>
