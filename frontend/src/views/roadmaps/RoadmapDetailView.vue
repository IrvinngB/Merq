<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { BaseButton, LoadingSpinner, MarkdownRenderer } from '@/components/common'
import RoadmapGraph from '@/components/roadmap/RoadmapGraph.vue'
import { useRoadmapsStore, useAuthStore } from '@/stores'
import { aiApi, roadmapsApi } from '@/api'
import type { RoadmapNode, NodeConnection } from '@/api'

const route = useRoute()
const roadmapsStore = useRoadmapsStore()
const authStore = useAuthStore()

const roadmapId = computed(() => Number(route.params.id))
const dashboardRoute = computed(() => `/${authStore.user?.username || ''}`)

const selectedNode = ref<RoadmapNode | null>(null)
const showNodePanel = ref(false)
const generatingContent = ref(false)
const generationError = ref<string | null>(null)

// Modo edición
const editMode = ref(false)
const showEditNodeModal = ref(false)
const showAddNodeModal = ref(false)
const showConnectionInfo = ref(false)
const selectedConnection = ref<{ connection: NodeConnection; fromNode: RoadmapNode; toNode: RoadmapNode } | null>(null)
const savingNode = ref(false)
const deletingNode = ref(false)

// Form para editar/crear nodo
const nodeForm = ref({
  title: '',
  description: '',
  level: 'beginner' as 'beginner' | 'intermediate' | 'advanced',
  order_index: 0
})

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

// Abrir modal para editar nodo
function openEditNodeModal() {
  if (!selectedNode.value) return
  nodeForm.value = {
    title: selectedNode.value.title,
    description: selectedNode.value.description || '',
    level: selectedNode.value.level,
    order_index: selectedNode.value.order_index
  }
  showEditNodeModal.value = true
}

// Abrir modal para crear nodo (con nivel opcional pre-seleccionado)
function openAddNodeModal(preSelectedLevel?: 'beginner' | 'intermediate' | 'advanced') {
  const maxOrder = Math.max(...roadmapsStore.nodes.map(n => n.order_index), 0)
  nodeForm.value = {
    title: '',
    description: '',
    level: preSelectedLevel || 'beginner',
    order_index: maxOrder + 1
  }
  showAddNodeModal.value = true
}

// Guardar edición de nodo
async function saveNodeEdit() {
  if (!selectedNode.value || !roadmapsStore.currentRoadmap) return
  
  savingNode.value = true
  try {
    const updated = await roadmapsApi.updateNode(
      roadmapsStore.currentRoadmap.id,
      selectedNode.value.id,
      nodeForm.value
    )
    selectedNode.value = updated.data
    await roadmapsStore.fetchRoadmap(roadmapId.value)
    showEditNodeModal.value = false
  } catch (err) {
    console.error('Error updating node:', err)
  } finally {
    savingNode.value = false
  }
}

// Crear nuevo nodo
async function createNode() {
  if (!roadmapsStore.currentRoadmap) return
  
  savingNode.value = true
  try {
    await roadmapsApi.createNode(roadmapsStore.currentRoadmap.id, nodeForm.value)
    await roadmapsStore.fetchRoadmap(roadmapId.value)
    showAddNodeModal.value = false
  } catch (err) {
    console.error('Error creating node:', err)
  } finally {
    savingNode.value = false
  }
}

// Eliminar nodo
async function deleteNode() {
  if (!selectedNode.value || !roadmapsStore.currentRoadmap) return
  if (!confirm(`¿Eliminar el nodo "${selectedNode.value.title}"?`)) return
  
  deletingNode.value = true
  try {
    await roadmapsApi.deleteNode(roadmapsStore.currentRoadmap.id, selectedNode.value.id)
    await roadmapsStore.fetchRoadmap(roadmapId.value)
    await roadmapsStore.fetchConnections(roadmapId.value)
    closeNodePanel()
  } catch (err) {
    console.error('Error deleting node:', err)
  } finally {
    deletingNode.value = false
  }
}

// Manejar click en conexión
function handleConnectionClick(connection: NodeConnection, fromNode: RoadmapNode, toNode: RoadmapNode) {
  selectedConnection.value = { connection, fromNode, toNode }
  showConnectionInfo.value = true
}

// Eliminar conexión
async function deleteConnection() {
  if (!selectedConnection.value || !roadmapsStore.currentRoadmap) return
  
  try {
    await roadmapsApi.deleteConnection(
      roadmapsStore.currentRoadmap.id,
      selectedConnection.value.connection.id
    )
    await roadmapsStore.fetchConnections(roadmapId.value)
    showConnectionInfo.value = false
    selectedConnection.value = null
  } catch (err) {
    console.error('Error deleting connection:', err)
  }
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

const levelColors: Record<string, { bg: string; text: string; border: string }> = {
  beginner: { bg: 'bg-emerald-500/10', text: 'text-emerald-500', border: 'border-emerald-500/30' },
  intermediate: { bg: 'bg-amber-500/10', text: 'text-amber-500', border: 'border-amber-500/30' },
  advanced: { bg: 'bg-rose-500/10', text: 'text-rose-500', border: 'border-rose-500/30' }
}

const togglingComplete = ref(false)

async function toggleComplete() {
  if (!selectedNode.value || !roadmapsStore.currentRoadmap) return
  
  togglingComplete.value = true
  try {
    const updated = await roadmapsStore.toggleNodeComplete(roadmapsStore.currentRoadmap.id, selectedNode.value.id)
    if (updated) {
      selectedNode.value = updated
    }
  } catch {
    // Error handled by store
  } finally {
    togglingComplete.value = false
  }
}

// Statistics computeds
const nodeStats = computed(() => {
  const nodes = roadmapsStore.nodes
  const total = nodes.length
  const completed = nodes.filter(n => n.is_completed).length
  const withContent = nodes.filter(n => n.content).length
  
  const byLevel = {
    beginner: nodes.filter(n => n.level === 'beginner').length,
    intermediate: nodes.filter(n => n.level === 'intermediate').length,
    advanced: nodes.filter(n => n.level === 'advanced').length
  }
  
  const completedByLevel = {
    beginner: nodes.filter(n => n.level === 'beginner' && n.is_completed).length,
    intermediate: nodes.filter(n => n.level === 'intermediate' && n.is_completed).length,
    advanced: nodes.filter(n => n.level === 'advanced' && n.is_completed).length
  }
  
  return {
    total,
    completed,
    withContent,
    progress: total > 0 ? Math.round((completed / total) * 100) : 0,
    byLevel,
    completedByLevel
  }
})
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
            
            <!-- Progress Stats -->
            <div class="flex flex-wrap items-center gap-4">
              <!-- Progress Bar -->
              <div class="flex items-center gap-3 bg-bg-secondary/50 rounded-xl px-4 py-2.5 border border-line">
                <div class="flex flex-col items-end">
                  <span class="text-xs text-text-secondary">Progreso</span>
                  <span class="text-lg font-bold text-text">{{ nodeStats.progress }}%</span>
                </div>
                <div class="w-24 h-2 bg-bg rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-gradient-to-r from-emerald-500 to-primary rounded-full transition-all duration-500"
                    :style="{ width: `${nodeStats.progress}%` }"
                  ></div>
                </div>
              </div>
              
              <!-- Level Stats -->
              <div class="flex items-center gap-2">
                <div 
                  v-for="(count, level) in nodeStats.byLevel" 
                  :key="level"
                  class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border"
                  :class="[levelColors[level as keyof typeof levelColors]?.bg, levelColors[level as keyof typeof levelColors]?.border]"
                >
                  <span 
                    class="w-2 h-2 rounded-full"
                    :class="{
                      'bg-emerald-500': level === 'beginner',
                      'bg-amber-500': level === 'intermediate',
                      'bg-rose-500': level === 'advanced'
                    }"
                  ></span>
                  <span class="text-sm font-medium" :class="levelColors[level as keyof typeof levelColors]?.text">
                    {{ nodeStats.completedByLevel[level as keyof typeof nodeStats.completedByLevel] }}/{{ count }}
                  </span>
                </div>
              </div>
              
              <!-- Edit Mode Toggle -->
              <div class="flex items-center gap-2">
                <button
                  @click="openAddNodeModal()"
                  v-if="editMode"
                  class="p-2 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                  title="Añadir nodo"
                >
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                </button>
                <button
                  @click="editMode = !editMode"
                  class="p-2 rounded-lg transition-colors"
                  :class="editMode 
                    ? 'bg-amber-500/20 text-amber-500 ring-2 ring-amber-500/30' 
                    : 'bg-bg-secondary text-text-secondary hover:text-text hover:bg-bg-secondary/80'"
                  :title="editMode ? 'Desactivar edición' : 'Activar edición'"
                >
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Graph -->
      <div class="h-[calc(100vh-280px)] p-4">
        <RoadmapGraph
          :nodes="roadmapsStore.nodes"
          :connections="roadmapsStore.connections"
          :edit-mode="editMode"
          @node-click="handleNodeClick"
          @connection-click="handleConnectionClick"
          @add-node="openAddNodeModal"
        />
      </div>

      <!-- Node Panel -->
      <Teleport to="body">
        <Transition
          enter-active-class="transition-opacity duration-200"
          enter-from-class="opacity-0"
          enter-to-class="opacity-100"
          leave-active-class="transition-opacity duration-200"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div v-if="showNodePanel && selectedNode" class="fixed inset-0 z-50 flex justify-end">
            <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="closeNodePanel" />
            <Transition
              enter-active-class="transition-transform duration-300 ease-out"
              enter-from-class="translate-x-full"
              enter-to-class="translate-x-0"
              leave-active-class="transition-transform duration-200 ease-in"
              leave-from-class="translate-x-0"
              leave-to-class="translate-x-full"
            >
              <div class="relative w-full max-w-xl bg-card border-l border-line h-full overflow-y-auto shadow-2xl">
                <!-- Panel Header -->
                <div class="sticky top-0 bg-card/95 backdrop-blur border-b border-line p-6 z-10">
                  <div class="flex items-start justify-between gap-4">
                    <div class="flex-1">
                      <div class="flex items-center gap-2 mb-3">
                        <span
                          class="text-xs font-bold px-3 py-1.5 rounded-full border"
                          :class="[levelColors[selectedNode.level]?.bg, levelColors[selectedNode.level]?.text, levelColors[selectedNode.level]?.border]"
                        >
                          {{ levelLabels[selectedNode.level] }}
                        </span>
                        <span v-if="selectedNode.is_completed" class="text-xs font-medium text-emerald-500 flex items-center gap-1">
                          <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                          </svg>
                          Completado
                        </span>
                      </div>
                      <h2 class="text-xl font-bold text-text">{{ selectedNode.title }}</h2>
                      <p v-if="selectedNode.description" class="text-text-secondary mt-2 text-sm leading-relaxed">
                        {{ selectedNode.description }}
                      </p>
                    </div>
                    <button
                      @click="closeNodePanel"
                      class="p-2 rounded-xl text-text-secondary hover:text-text hover:bg-line/50 transition-colors"
                    >
                      <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  
                  <!-- Complete Button in Header -->
                  <div v-if="selectedNode.content" class="mt-4 pt-4 border-t border-line/50">
                    <button
                      @click="toggleComplete"
                      :disabled="togglingComplete"
                      class="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-medium transition-all duration-200"
                      :class="selectedNode.is_completed 
                        ? 'bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20 border border-emerald-500/30' 
                        : 'bg-bg-secondary hover:bg-line text-text-secondary hover:text-text border border-line'"
                    >
                      <svg v-if="togglingComplete" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <svg v-else-if="selectedNode.is_completed" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                      <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {{ selectedNode.is_completed ? 'Completado' : 'Marcar como completado' }}
                    </button>
                  </div>
                </div>

                <!-- Panel Content -->
                <div class="p-6">
                  <!-- No content yet -->
                  <div v-if="!selectedNode.content" class="text-center py-16">
                    <div class="w-20 h-20 bg-gradient-to-br from-primary/20 to-primary-hover/20 rounded-3xl flex items-center justify-center mx-auto mb-6">
                      <svg class="w-10 h-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <h3 class="text-xl font-bold text-text mb-2">Contenido no generado</h3>
                    <p class="text-text-secondary text-sm mb-8 max-w-sm mx-auto">
                      Genera el contenido de este tema con IA para ver una guía detallada de aprendizaje
                    </p>
                    
                    <div v-if="generationError" class="mb-6 p-4 bg-danger/10 border border-danger/20 rounded-xl text-danger text-sm max-w-sm mx-auto">
                      {{ generationError }}
                    </div>

                    <BaseButton size="lg" @click="generateNodeContent" :loading="generatingContent">
                      <svg v-if="!generatingContent" class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      {{ generatingContent ? 'Generando contenido...' : 'Generar con IA' }}
                    </BaseButton>
                    
                    <p v-if="generatingContent" class="text-text-secondary text-xs mt-4">
                      Esto puede tomar unos segundos...
                    </p>
                  </div>

                  <!-- Content -->
                  <div v-else class="prose-custom">
                    <MarkdownRenderer :content="selectedNode.content" />
                  </div>
                  
                  <!-- Edit/Delete buttons -->
                  <div v-if="editMode" class="mt-8 pt-6 border-t border-line flex items-center gap-3">
                    <button
                      @click="openEditNodeModal"
                      class="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-primary/10 text-primary hover:bg-primary/20 font-medium transition-colors"
                    >
                      <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                      Editar nodo
                    </button>
                    <button
                      @click="deleteNode"
                      :disabled="deletingNode"
                      class="flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-danger/10 text-danger hover:bg-danger/20 font-medium transition-colors"
                    >
                      <svg v-if="deletingNode" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </Transition>
      </Teleport>
      
      <!-- Edit Node Modal -->
      <Teleport to="body">
        <Transition
          enter-active-class="transition-opacity duration-200"
          enter-from-class="opacity-0"
          enter-to-class="opacity-100"
          leave-active-class="transition-opacity duration-200"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div v-if="showEditNodeModal" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showEditNodeModal = false" />
            <div class="relative w-full max-w-md bg-card rounded-2xl shadow-2xl border border-line p-6">
              <h3 class="text-xl font-bold text-text mb-6">Editar nodo</h3>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-text mb-2">Título</label>
                  <input
                    v-model="nodeForm.title"
                    type="text"
                    class="w-full px-4 py-2.5 bg-bg border border-line rounded-xl text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-text mb-2">Descripción</label>
                  <textarea
                    v-model="nodeForm.description"
                    rows="3"
                    class="w-full px-4 py-2.5 bg-bg border border-line rounded-xl text-text focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-text mb-2">Nivel</label>
                  <select
                    v-model="nodeForm.level"
                    class="w-full px-4 py-2.5 bg-bg border border-line rounded-xl text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                  >
                    <option value="beginner">Principiante</option>
                    <option value="intermediate">Intermedio</option>
                    <option value="advanced">Avanzado</option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-text mb-2">Orden</label>
                  <input
                    v-model.number="nodeForm.order_index"
                    type="number"
                    min="0"
                    class="w-full px-4 py-2.5 bg-bg border border-line rounded-xl text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
              </div>
              
              <div class="flex items-center gap-3 mt-6">
                <button
                  @click="showEditNodeModal = false"
                  class="flex-1 px-4 py-2.5 rounded-xl border border-line text-text-secondary hover:text-text hover:bg-bg-secondary transition-colors"
                >
                  Cancelar
                </button>
                <BaseButton @click="saveNodeEdit" :loading="savingNode" class="flex-1">
                  Guardar
                </BaseButton>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
      
      <!-- Add Node Modal -->
      <Teleport to="body">
        <Transition
          enter-active-class="transition-opacity duration-200"
          enter-from-class="opacity-0"
          enter-to-class="opacity-100"
          leave-active-class="transition-opacity duration-200"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div v-if="showAddNodeModal" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showAddNodeModal = false" />
            <div class="relative w-full max-w-md bg-card rounded-2xl shadow-2xl border border-line p-6">
              <h3 class="text-xl font-bold text-text mb-6">Añadir nodo</h3>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-text mb-2">Título</label>
                  <input
                    v-model="nodeForm.title"
                    type="text"
                    placeholder="Nombre del tema"
                    class="w-full px-4 py-2.5 bg-bg border border-line rounded-xl text-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-text mb-2">Descripción</label>
                  <textarea
                    v-model="nodeForm.description"
                    rows="3"
                    placeholder="Breve descripción del tema"
                    class="w-full px-4 py-2.5 bg-bg border border-line rounded-xl text-text focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-text mb-2">Nivel</label>
                  <div class="flex gap-2">
                    <button
                      v-for="level in ['beginner', 'intermediate', 'advanced']"
                      :key="level"
                      @click="nodeForm.level = level as 'beginner' | 'intermediate' | 'advanced'"
                      class="flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all"
                      :class="nodeForm.level === level 
                        ? [levelColors[level]?.bg, levelColors[level]?.text, 'ring-2', levelColors[level]?.border.replace('border-', 'ring-')]
                        : 'bg-bg-secondary text-text-secondary hover:text-text'"
                    >
                      {{ levelLabels[level] }}
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="flex items-center gap-3 mt-6">
                <button
                  @click="showAddNodeModal = false"
                  class="flex-1 px-4 py-2.5 rounded-xl border border-line text-text-secondary hover:text-text hover:bg-bg-secondary transition-colors"
                >
                  Cancelar
                </button>
                <BaseButton @click="createNode" :loading="savingNode" :disabled="!nodeForm.title.trim()" class="flex-1">
                  Crear nodo
                </BaseButton>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
      
      <!-- Connection Info Modal -->
      <Teleport to="body">
        <Transition
          enter-active-class="transition-opacity duration-200"
          enter-from-class="opacity-0"
          enter-to-class="opacity-100"
          leave-active-class="transition-opacity duration-200"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div v-if="showConnectionInfo && selectedConnection" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showConnectionInfo = false" />
            <div class="relative w-full max-w-sm bg-card rounded-2xl shadow-2xl border border-line p-6">
              <h3 class="text-lg font-bold text-text mb-4">Conexión</h3>
              
              <div class="flex items-center gap-3 p-4 bg-bg rounded-xl mb-6">
                <div class="flex-1">
                  <span 
                    class="text-xs font-medium px-2 py-0.5 rounded-full mb-1 inline-block"
                    :class="[levelColors[selectedConnection.fromNode.level]?.bg, levelColors[selectedConnection.fromNode.level]?.text]"
                  >
                    {{ levelLabels[selectedConnection.fromNode.level] }}
                  </span>
                  <p class="text-sm font-medium text-text">{{ selectedConnection.fromNode.title }}</p>
                </div>
                <svg class="w-6 h-6 text-text-secondary flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
                <div class="flex-1 text-right">
                  <span 
                    class="text-xs font-medium px-2 py-0.5 rounded-full mb-1 inline-block"
                    :class="[levelColors[selectedConnection.toNode.level]?.bg, levelColors[selectedConnection.toNode.level]?.text]"
                  >
                    {{ levelLabels[selectedConnection.toNode.level] }}
                  </span>
                  <p class="text-sm font-medium text-text">{{ selectedConnection.toNode.title }}</p>
                </div>
              </div>
              
              <p class="text-sm text-text-secondary mb-6 text-center">
                Esta conexión indica que <strong class="text-text">{{ selectedConnection.fromNode.title }}</strong> es prerrequisito de <strong class="text-text">{{ selectedConnection.toNode.title }}</strong>
              </p>
              
              <div class="flex items-center gap-3">
                <button
                  @click="showConnectionInfo = false"
                  class="flex-1 px-4 py-2.5 rounded-xl border border-line text-text-secondary hover:text-text hover:bg-bg-secondary transition-colors"
                >
                  Cerrar
                </button>
                <button
                  v-if="editMode"
                  @click="deleteConnection"
                  class="flex-1 px-4 py-2.5 rounded-xl bg-danger/10 text-danger hover:bg-danger/20 font-medium transition-colors"
                >
                  Eliminar conexión
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
    </template>
  </div>
</template>
