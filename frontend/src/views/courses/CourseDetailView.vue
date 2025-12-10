<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { BaseButton, BaseInput, BaseTextarea, LoadingSpinner } from '@/components/common'
import { useCoursesStore, useAuthStore } from '@/stores'
import type { ModuleCreate } from '@/types'

const route = useRoute()
const router = useRouter()
const coursesStore = useCoursesStore()
const authStore = useAuthStore()

const courseId = computed(() => Number(route.params.id))
const dashboardRoute = computed(() => `/${authStore.user?.username || ''}`)
const courseRoute = computed(() => `/${authStore.user?.username}/courses/${courseId.value}`)

const showCreateModuleModal = ref(false)
const newModule = ref<ModuleCreate>({ title: '', description: '' })

const firstModuleRoute = computed(() => {
  const firstModule = coursesStore.modules[0]
  if (!firstModule) return null
  return `${courseRoute.value}/modules/${firstModule.id}`
})

function handleStartStudying() {
  if (firstModuleRoute.value) {
    router.push(firstModuleRoute.value)
  }
}

onMounted(async () => {
  await coursesStore.fetchCourse(courseId.value)
  await coursesStore.fetchModules(courseId.value)
})

onUnmounted(() => {
  coursesStore.clearCurrent()
})

async function handleCreateModule() {
  if (!newModule.value.title.trim()) return
  try {
    await coursesStore.createModule(courseId.value, newModule.value)
    showCreateModuleModal.value = false
    newModule.value = { title: '', description: '' }
  } catch {
    // error manejado en store
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-180px)]">
    <!-- Loading -->
    <div v-if="coursesStore.loading" class="flex items-center justify-center py-24">
      <LoadingSpinner size="lg" />
    </div>

    <!-- Error -->
    <div v-else-if="coursesStore.error" class="max-w-md mx-auto text-center py-24 px-4">
      <div class="w-20 h-20 bg-danger/10 rounded-3xl flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h2 class="text-xl font-bold text-text mb-2">Error al cargar el curso</h2>
      <p class="text-text-secondary mb-6">{{ coursesStore.error }}</p>
      <RouterLink :to="dashboardRoute">
        <BaseButton variant="secondary">Volver al dashboard</BaseButton>
      </RouterLink>
    </div>

    <!-- Content -->
    <template v-else-if="coursesStore.currentCourse">
      <!-- Header -->
      <div class="bg-gradient-to-br from-primary/5 via-bg to-primary-hover/5 border-b border-line">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
          <RouterLink
            :to="dashboardRoute"
            class="inline-flex items-center gap-2 text-text-secondary hover:text-text text-sm mb-6 transition-colors group"
          >
            <svg class="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            Volver al dashboard
          </RouterLink>
          
          <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
            <div class="flex items-start gap-5">
              <div class="w-16 h-16 bg-gradient-to-br from-primary to-primary-hover rounded-2xl flex items-center justify-center shadow-lg shadow-primary/25 flex-shrink-0">
                <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div>
                <div class="flex items-center gap-3 mb-2">
                  <span class="text-xs font-medium text-primary bg-primary/10 px-2.5 py-1 rounded-full">En progreso</span>
                </div>
                <h1 class="text-2xl md:text-3xl font-bold text-text">{{ coursesStore.currentCourse.title }}</h1>
                <p class="text-text-secondary mt-2 max-w-2xl">{{ coursesStore.currentCourse.description }}</p>
              </div>
            </div>
            <BaseButton 
              v-if="coursesStore.modules.length > 0"
              size="lg" 
              class="group flex-shrink-0"
              @click="handleStartStudying"
            >
              <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Comenzar a estudiar
              <svg class="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </BaseButton>
          </div>
        </div>
      </div>

      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid lg:grid-cols-3 gap-8">
          <!-- Módulos -->
          <div class="lg:col-span-2">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-bold text-text">Módulos del curso</h2>
              <BaseButton size="sm" @click="showCreateModuleModal = true">
                <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Nuevo módulo
              </BaseButton>
            </div>

            <div v-if="coursesStore.modules.length === 0" class="bg-card border border-line rounded-2xl p-12 text-center">
              <div class="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <p class="text-text font-medium mb-2">No hay módulos</p>
              <p class="text-text-secondary text-sm mb-6">Crea el primer módulo para este curso</p>
              <BaseButton @click="showCreateModuleModal = true">
                <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Crear módulo
              </BaseButton>
            </div>

            <div v-else class="space-y-4">
              <RouterLink
                v-for="(module, index) in coursesStore.modules"
                :key="module.id"
                :to="`${courseRoute}/modules/${module.id}`"
                class="block bg-card border border-line rounded-2xl p-5 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5 transition-all cursor-pointer group hover:-translate-y-1"
              >
                <div class="flex items-start justify-between">
                  <div class="flex items-start gap-4">
                    <div class="w-12 h-12 bg-gradient-to-br from-primary/20 to-primary/10 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:from-primary group-hover:to-primary-hover transition-all">
                      <span class="text-primary font-bold group-hover:text-white transition-colors">{{ index + 1 }}</span>
                    </div>
                    <div>
                      <h3 class="font-bold text-text group-hover:text-primary transition-colors">{{ module.title }}</h3>
                      <p v-if="module.description" class="text-sm text-text-secondary mt-1 line-clamp-2">
                        {{ module.description }}
                      </p>
                    </div>
                  </div>
                  <svg class="w-5 h-5 text-text-secondary flex-shrink-0 group-hover:text-primary group-hover:translate-x-1 transition-all mt-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </RouterLink>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="space-y-6">
            <!-- Progreso -->
            <div class="bg-card border border-line rounded-2xl p-6">
              <h3 class="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">Tu progreso</h3>
              <div class="space-y-4">
                <div>
                  <div class="flex justify-between text-sm mb-2">
                    <span class="text-text-secondary">Completado</span>
                    <span class="text-text font-bold">0%</span>
                  </div>
                  <div class="h-3 bg-bg-secondary rounded-full overflow-hidden">
                    <div class="h-full bg-gradient-to-r from-primary to-primary-hover rounded-full transition-all" style="width: 0%" />
                  </div>
                </div>

                <div class="grid grid-cols-3 gap-3 pt-4">
                  <div class="text-center p-3 bg-bg-secondary rounded-xl">
                    <p class="text-2xl font-bold text-text">{{ coursesStore.modules.length }}</p>
                    <p class="text-xs text-text-secondary">Módulos</p>
                  </div>
                  <div class="text-center p-3 bg-bg-secondary rounded-xl">
                    <p class="text-2xl font-bold text-text">--</p>
                    <p class="text-xs text-text-secondary">Lecciones</p>
                  </div>
                  <div class="text-center p-3 bg-bg-secondary rounded-xl">
                    <p class="text-2xl font-bold text-text">--</p>
                    <p class="text-xs text-text-secondary">Preguntas</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Acciones -->
            <div class="bg-gradient-to-br from-primary/10 to-primary-hover/10 border border-primary/20 rounded-2xl p-6">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 bg-primary/20 rounded-xl flex items-center justify-center">
                  <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <h3 class="font-semibold text-text">Aprendizaje adaptativo</h3>
                </div>
              </div>
              <p class="text-sm text-text-secondary mb-4">
                La dificultad se ajusta automáticamente según tu rendimiento.
              </p>
              <BaseButton class="w-full group">
                Comenzar a estudiar
                <svg class="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Modal: Crear módulo -->
    <Teleport to="body">
      <div v-if="showCreateModuleModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50" @click="showCreateModuleModal = false" />
        <div class="relative bg-card border border-line rounded-2xl p-6 w-full max-w-md shadow-xl">
          <h3 class="text-lg font-bold text-text mb-4">Nuevo módulo</h3>
          <form @submit.prevent="handleCreateModule" class="space-y-4">
            <BaseInput
              v-model="newModule.title"
              label="Título"
              placeholder="Ej: Introducción a los conceptos básicos"
              required
            />
            <BaseTextarea
              v-model="newModule.description"
              label="Descripción (opcional)"
              placeholder="Describe brevemente el contenido del módulo..."
              :rows="3"
            />
            <div class="flex justify-end gap-3 pt-2">
              <BaseButton type="button" variant="secondary" @click="showCreateModuleModal = false">
                Cancelar
              </BaseButton>
              <BaseButton type="submit" :disabled="!newModule.title.trim() || coursesStore.loading">
                {{ coursesStore.loading ? 'Creando...' : 'Crear módulo' }}
              </BaseButton>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
