<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { BaseButton, LoadingSpinner } from '@/components/common'
import { useAuthStore, useRoadmapsStore } from '@/stores'

const authStore = useAuthStore()
const roadmapsStore = useRoadmapsStore()

const showDeleteConfirm = ref(false)
const roadmapToDelete = ref<{ id: number; title: string } | null>(null)

const userRoutes = computed(() => {
  const username = authStore.user?.username || ''
  return {
    roadmapsNew: `/${username}/roadmaps/new`,
    roadmap: (id: number) => `/${username}/roadmaps/${id}`
  }
})

onMounted(() => {
  if (authStore.user?.id) {
    roadmapsStore.fetchMyRoadmaps(authStore.user.id)
  }
})

function openDeleteConfirm(roadmap: { id: number; title: string }, event: Event) {
  event.preventDefault()
  event.stopPropagation()
  roadmapToDelete.value = roadmap
  showDeleteConfirm.value = true
}

async function handleDeleteRoadmap() {
  if (!roadmapToDelete.value) return
  try {
    await roadmapsStore.deleteRoadmap(roadmapToDelete.value.id)
    showDeleteConfirm.value = false
    roadmapToDelete.value = null
  } catch {
    // error manejado en store
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-180px)]">
    <!-- Header con gradiente -->
    <div class="bg-gradient-to-br from-primary/5 via-bg to-primary-hover/5 border-b border-line">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div class="flex items-center gap-5">
            <div class="w-16 h-16 bg-gradient-to-br from-primary to-primary-hover rounded-2xl flex items-center justify-center shadow-lg shadow-primary/25">
              <span class="text-white font-bold text-2xl">
                {{ authStore.user?.full_name?.charAt(0)?.toUpperCase() || 'U' }}
              </span>
            </div>
            <div>
              <h1 class="text-2xl md:text-3xl font-bold text-text">
                Hola, {{ authStore.user?.full_name?.split(' ')[0] || 'Usuario' }} 👋
              </h1>
              <p class="text-text-secondary mt-1">@{{ authStore.user?.username }}</p>
            </div>
          </div>
          <RouterLink :to="userRoutes.roadmapsNew">
            <BaseButton size="lg" class="group w-full md:w-auto">
              <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Crear roadmap
              <svg class="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </BaseButton>
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Stats cards -->
      <div class="grid md:grid-cols-3 gap-6 mb-10">
        <div class="bg-card border border-line rounded-2xl p-6 hover:shadow-lg hover:shadow-primary/5 transition-all hover:-translate-y-1">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-gradient-to-br from-primary/20 to-primary/10 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <span class="text-xs font-medium text-primary bg-primary/10 px-2.5 py-1 rounded-full">Activos</span>
          </div>
          <p class="text-3xl font-bold text-text mb-1">{{ roadmapsStore.roadmaps.length }}</p>
          <p class="text-sm text-text-secondary">Roadmaps creados</p>
        </div>

        <div class="bg-card border border-line rounded-2xl p-6 hover:shadow-lg hover:shadow-success/5 transition-all hover:-translate-y-1">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-gradient-to-br from-success/20 to-success/10 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span class="text-xs font-medium text-success bg-success/10 px-2.5 py-1 rounded-full">Progreso</span>
          </div>
          <p class="text-3xl font-bold text-text mb-1">0</p>
          <p class="text-sm text-text-secondary">Nodos completados</p>
        </div>

        <div class="bg-card border border-line rounded-2xl p-6 hover:shadow-lg hover:shadow-warning/5 transition-all hover:-translate-y-1">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-gradient-to-br from-warning/20 to-warning/10 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span class="text-xs font-medium text-warning bg-warning/10 px-2.5 py-1 rounded-full">IA</span>
          </div>
          <p class="text-3xl font-bold text-text mb-1">Ollama</p>
          <p class="text-sm text-text-secondary">Generación local</p>
        </div>
      </div>

      <!-- Roadmaps section -->
      <div class="mb-6 flex items-center justify-between">
        <h2 class="text-xl font-bold text-text">Mis roadmaps</h2>
        <span class="text-sm text-text-secondary">{{ roadmapsStore.roadmaps.length }} roadmap(s)</span>
      </div>

      <div v-if="roadmapsStore.loading" class="py-16">
        <LoadingSpinner size="lg" />
      </div>

      <!-- Empty state -->
      <div v-else-if="roadmapsStore.roadmaps.length === 0" class="relative">
        <div class="bg-gradient-to-br from-primary/5 to-primary-hover/5 border-2 border-dashed border-primary/20 rounded-3xl p-12 text-center">
          <div class="w-24 h-24 bg-gradient-to-br from-primary/20 to-primary-hover/20 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <svg class="w-12 h-12 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-text mb-3">Crea tu primer roadmap</h3>
          <p class="text-text-secondary mb-8 max-w-md mx-auto">
            Sube un PDF o pega texto y nuestra IA generará un roadmap interactivo con temas organizados por nivel de dificultad.
          </p>
          <RouterLink :to="userRoutes.roadmapsNew">
            <BaseButton size="lg" class="group">
              <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Crear mi primer roadmap
              <svg class="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </BaseButton>
          </RouterLink>
        </div>
      </div>

      <!-- Grid de roadmaps -->
      <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <RouterLink
          v-for="roadmap in roadmapsStore.roadmaps"
          :key="roadmap.id"
          :to="userRoutes.roadmap(roadmap.id)"
          class="group"
        >
          <div class="bg-card border border-line rounded-2xl overflow-hidden hover:shadow-xl hover:shadow-primary/10 transition-all hover:-translate-y-2">
            <div class="aspect-video bg-gradient-to-br from-primary/20 via-primary/10 to-primary-hover/20 flex items-center justify-center relative overflow-hidden">
              <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRjMC0yLjIxLTEuNzktNC00LTRzLTQgMS43OS00IDQgMS43OSA0IDQgNCA0LTEuNzkgNC00eiIvPjwvZz48L2c+PC9zdmc+')] opacity-50" />
              <svg class="w-16 h-16 text-primary/30 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <div class="p-5">
              <div class="flex items-center justify-between mb-3">
                <span class="text-xs font-medium text-primary bg-primary/10 px-2.5 py-1 rounded-full">Roadmap</span>
                <button
                  @click="openDeleteConfirm({ id: roadmap.id, title: roadmap.title }, $event)"
                  class="p-1.5 rounded-lg text-text-secondary hover:text-danger hover:bg-danger/10 transition-colors opacity-0 group-hover:opacity-100"
                  title="Eliminar roadmap"
                >
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
              <h3 class="text-lg font-bold text-text mb-2 group-hover:text-primary transition-colors">{{ roadmap.title }}</h3>
              <p class="text-text-secondary text-sm line-clamp-2 mb-4">
                {{ roadmap.description || 'Sin descripción' }}
              </p>
              <div class="flex items-center justify-between text-sm">
                <span class="text-text-secondary">Explorar</span>
                <span class="text-primary font-medium group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                  Ver roadmap
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </span>
              </div>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>

    <!-- Modal: Confirmar eliminación -->
    <Teleport to="body">
      <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50" @click="showDeleteConfirm = false" />
        <div class="relative bg-card border border-line rounded-2xl p-6 w-full max-w-md shadow-2xl">
          <div class="w-14 h-14 bg-danger/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-7 h-7 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-text text-center mb-2">¿Eliminar roadmap?</h3>
          <p class="text-text-secondary text-center mb-6">
            Se eliminará <strong class="text-text">{{ roadmapToDelete?.title }}</strong> y todo su contenido. Esta acción no se puede deshacer.
          </p>
          <div class="flex gap-3">
            <BaseButton variant="secondary" class="flex-1" @click="showDeleteConfirm = false">
              Cancelar
            </BaseButton>
            <BaseButton variant="danger" class="flex-1" @click="handleDeleteRoadmap" :loading="roadmapsStore.loading">
              Eliminar
            </BaseButton>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
