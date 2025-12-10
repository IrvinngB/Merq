<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { BaseButton, LoadingSpinner, MarkdownRenderer } from '@/components/common'
import RoadmapGraph from '@/components/roadmap/RoadmapGraph.vue'
import { useRoadmapsStore, useAuthStore } from '@/stores'
import { aiApi } from '@/api'
import type { RoadmapNode } from '@/api'

const route = useRoute()
const router = useRouter()
const roadmapsStore = useRoadmapsStore()
const authStore = useAuthStore()

const roadmapId = computed(() => Number(route.params.id))
const dashboardRoute = computed(() => `/${authStore.user?.username || ''}`)

const selectedNode = ref<RoadmapNode | null>(null)
const showNodePanel = ref(false)
const generatingContent = ref(false)
const generationError = ref<string | null>(null)

onMounted(async () => {
  await roadmapsStore.fetchRoadmap(roadmapId.value)
  await roadmapsStore.fetchConnections(roadmapId.value)
})

onUnmounted(() => {
  roadmapsStore.clearCurrent()
})

function handleNodeClick(node: RoadmapNode) {
  selectedNode.value = node
  showNodePanel.value = true
}

function closeNodePanel() {
  showNodePanel.value = false
  selectedNode.value = null
}

async function generateNodeContent() {
  if (!selectedNode.value) return
  
  generatingContent.value = true
  generationError.value = null
  
  try {
    await aiApi.generateNodeContent(selectedNode.value.id)
    await roadmapsStore.fetchRoadmap(roadmapId.value)
    const updatedNode = roadmapsStore.nodes.find(n => n.id === selectedNode.value?.id)
    if (updatedNode) {
      selectedNode.value = updatedNode
    }
  } catch (err: unknown) {
    const error = err as { response?: { data?: { detail?: string } } }
    generationError.value = error.response?.data?.detail || 'Error al generar contenido'
  } finally {
    generatingContent.value = false
  }
}

const levelLabels: Record<string, string> = {
  beginner: 'Principiante',
  intermediate: 'Intermedio',
  advanced: 'Avanzado'
}

const levelColors: Record<string, { bg: string; text: string }> = {
  beginner: { bg: 'bg-success/10', text: 'text-success' },
  intermediate: { bg: 'bg-warning/10', text: 'text-warning' },
  advanced: { bg: 'bg-danger/10', text: 'text-danger' }
}
</script>

<template>
  <div class="min-h-[calc(100vh-180px)]">
    <!-- Loading -->
    <div v-if="roadmapsStore.loading && !roadmapsStore.currentRoadmap" class="flex items-center justify-center py-24">
      <LoadingSpinner size="lg" />
    </div>

    <!-- Error -->
    <div v-else-if="roadmapsStore.error" class="max-w-md mx-auto text-center py-24 px-4">
      <div class="w-20 h-20 bg-danger/10 rounded-3xl flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h2 class="text-xl font-bold text-text mb-2">Error al cargar el roadmap</h2>
      <p class="text-text-secondary mb-6">{{ roadmapsStore.error }}</p>
      <RouterLink :to="dashboardRoute">
        <BaseButton variant="secondary">Volver al dashboard</BaseButton>
      </RouterLink>
    </div>

    <!-- Content -->
    <template v-else-if="roadmapsStore.currentRoadmap">
      <!-- Header -->
      <div class="bg-gradient-to-br from-primary/5 via-bg to-primary-hover/5 border-b border-line">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <RouterLink
            :to="dashboardRoute"
            class="inline-flex items-center gap-2 text-text-secondary hover:text-text text-sm mb-4 transition-colors group"
          >
            <svg class="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            Volver al dashboard
          </RouterLink>
          
          <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 class="text-2xl md:text-3xl font-bold text-text">{{ roadmapsStore.currentRoadmap.title }}</h1>
              <p v-if="roadmapsStore.currentRoadmap.description" class="text-text-secondary mt-1">
                {{ roadmapsStore.currentRoadmap.description }}
              </p>
            </div>
            <div class="flex items-center gap-3 text-sm text-text-secondary">
              <span class="flex items-center gap-1.5">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                {{ roadmapsStore.nodes.length }} nodos
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Graph -->
      <div class="h-[calc(100vh-280px)] p-4">
        <RoadmapGraph
          :nodes="roadmapsStore.nodes"
          :connections="roadmapsStore.connections"
          @node-click="handleNodeClick"
        />
      </div>

      <!-- Node Panel -->
      <Teleport to="body">
        <div v-if="showNodePanel && selectedNode" class="fixed inset-0 z-50 flex justify-end">
          <div class="absolute inset-0 bg-black/50" @click="closeNodePanel" />
          <div class="relative w-full max-w-xl bg-card border-l border-line h-full overflow-y-auto">
            <!-- Panel Header -->
            <div class="sticky top-0 bg-card border-b border-line p-6 z-10">
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <span
                      class="text-xs font-medium px-2.5 py-1 rounded-full"
                      :class="[levelColors[selectedNode.level].bg, levelColors[selectedNode.level].text]"
                    >
                      {{ levelLabels[selectedNode.level] }}
                    </span>
                  </div>
                  <h2 class="text-xl font-bold text-text">{{ selectedNode.title }}</h2>
                  <p v-if="selectedNode.description" class="text-text-secondary mt-1">
                    {{ selectedNode.description }}
                  </p>
                </div>
                <button
                  @click="closeNodePanel"
                  class="p-2 rounded-lg text-text-secondary hover:text-text hover:bg-line/50 transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Panel Content -->
            <div class="p-6">
              <!-- No content yet -->
              <div v-if="!selectedNode.content" class="text-center py-12">
                <div class="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-text mb-2">Contenido no generado</h3>
                <p class="text-text-secondary text-sm mb-6">
                  Genera el contenido de este tema para ver qué investigar
                </p>
                
                <div v-if="generationError" class="mb-4 p-3 bg-danger/10 border border-danger/20 rounded-xl text-danger text-sm">
                  {{ generationError }}
                </div>

                <BaseButton @click="generateNodeContent" :loading="generatingContent">
                  <svg v-if="!generatingContent" class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  {{ generatingContent ? 'Generando...' : 'Generar contenido' }}
                </BaseButton>
              </div>

              <!-- Content -->
              <div v-else>
                <MarkdownRenderer :content="selectedNode.content" />
              </div>
            </div>
          </div>
        </div>
      </Teleport>
    </template>
  </div>
</template>
