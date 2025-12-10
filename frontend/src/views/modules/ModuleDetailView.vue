<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { BaseButton, BaseInput, BaseTextarea, LoadingSpinner } from '@/components/common'
import { useCoursesStore, useAuthStore } from '@/stores'
import { aiApi } from '@/api'
import type { LessonCreate } from '@/types'
import type { AxiosError } from 'axios'

const route = useRoute()
const router = useRouter()
const coursesStore = useCoursesStore()
const authStore = useAuthStore()

const courseId = computed(() => Number(route.params.id))
const moduleId = computed(() => Number(route.params.moduleId))
const dashboardRoute = computed(() => `/${authStore.user?.username || ''}`)
const courseRoute = computed(() => `/${authStore.user?.username}/courses/${courseId.value}`)

const showCreateLessonModal = ref(false)
const showEditModuleModal = ref(false)
const showDeleteConfirm = ref(false)
const lessonToDelete = ref<number | null>(null)

const generatingContent = ref(false)
const generateError = ref('')

const newLesson = ref<LessonCreate>({ title: '', content: '' })
const editModuleData = ref({ title: '', description: '' })

const needsContentGeneration = computed(() => {
  if (coursesStore.lessons.length === 0) return false
  return coursesStore.lessons.every(lesson => !lesson.content)
})

onMounted(async () => {
  await Promise.all([
    coursesStore.fetchCourse(courseId.value),
    coursesStore.fetchModule(courseId.value, moduleId.value),
    coursesStore.fetchLessons(moduleId.value)
  ])
  if (coursesStore.currentModule) {
    editModuleData.value = {
      title: coursesStore.currentModule.title,
      description: coursesStore.currentModule.description || ''
    }
  }
})

onUnmounted(() => {
  coursesStore.clearModule()
})

async function handleCreateLesson() {
  if (!newLesson.value.title.trim()) return
  try {
    const lesson = await coursesStore.createLesson(moduleId.value, newLesson.value)
    showCreateLessonModal.value = false
    newLesson.value = { title: '', content: '' }
    router.push(`${courseRoute.value}/modules/${moduleId.value}/lessons/${lesson.id}`)
  } catch {
    // error manejado en store
  }
}

async function handleUpdateModule() {
  if (!editModuleData.value.title.trim()) return
  try {
    await coursesStore.updateModule(courseId.value, moduleId.value, editModuleData.value)
    showEditModuleModal.value = false
  } catch {
    // error manejado en store
  }
}

async function handleDeleteModule() {
  try {
    await coursesStore.deleteModule(courseId.value, moduleId.value)
    router.push(courseRoute.value)
  } catch {
    // error manejado en store
  }
}

async function handleDeleteLesson() {
  if (!lessonToDelete.value) return
  try {
    await coursesStore.deleteLesson(moduleId.value, lessonToDelete.value)
    lessonToDelete.value = null
    showDeleteConfirm.value = false
  } catch {
    // error manejado en store
  }
}

function openDeleteLessonConfirm(lessonId: number) {
  lessonToDelete.value = lessonId
  showDeleteConfirm.value = true
}

async function handleGenerateContent() {
  generatingContent.value = true
  generateError.value = ''
  try {
    await aiApi.generateModuleContent(moduleId.value)
    await coursesStore.fetchLessons(moduleId.value)
  } catch (err) {
    const axiosError = err as AxiosError<{ detail?: string }>
    generateError.value = axiosError.response?.data?.detail || 'Error al generar contenido'
  } finally {
    generatingContent.value = false
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-180px)]">
    <!-- Loading -->
    <div v-if="coursesStore.loading && !coursesStore.currentModule" class="flex items-center justify-center py-24">
      <LoadingSpinner size="lg" />
    </div>

    <!-- Error -->
    <div v-else-if="coursesStore.error && !coursesStore.currentModule" class="max-w-md mx-auto text-center py-24 px-4">
      <div class="w-20 h-20 bg-danger/10 rounded-3xl flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h2 class="text-xl font-bold text-text mb-2">Error al cargar el módulo</h2>
      <p class="text-text-secondary mb-6">{{ coursesStore.error }}</p>
      <RouterLink :to="courseRoute">
        <BaseButton variant="secondary">Volver al curso</BaseButton>
      </RouterLink>
    </div>

    <!-- Content -->
    <template v-else-if="coursesStore.currentModule">
      <!-- Header -->
      <div class="bg-gradient-to-br from-primary/5 via-bg to-primary-hover/5 border-b border-line">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <!-- Breadcrumb -->
          <nav class="flex items-center gap-2 text-sm text-text-secondary mb-6">
            <RouterLink :to="dashboardRoute" class="hover:text-text transition-colors">Dashboard</RouterLink>
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <RouterLink :to="courseRoute" class="hover:text-text transition-colors">
              {{ coursesStore.currentCourse?.title || 'Curso' }}
            </RouterLink>
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span class="text-text">{{ coursesStore.currentModule.title }}</span>
          </nav>

          <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
            <div class="flex items-start gap-5">
              <div class="w-14 h-14 bg-gradient-to-br from-primary to-primary-hover rounded-2xl flex items-center justify-center shadow-lg shadow-primary/25 flex-shrink-0">
                <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <div>
                <h1 class="text-2xl md:text-3xl font-bold text-text">{{ coursesStore.currentModule.title }}</h1>
                <p v-if="coursesStore.currentModule.description" class="text-text-secondary mt-2 max-w-2xl">
                  {{ coursesStore.currentModule.description }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <BaseButton variant="secondary" size="sm" @click="showEditModuleModal = true">
                <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Editar
              </BaseButton>
              <BaseButton variant="danger" size="sm" @click="showDeleteConfirm = true; lessonToDelete = null">
                <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Eliminar
              </BaseButton>
            </div>
          </div>
        </div>
      </div>

      <!-- Lecciones -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Banner: Generar contenido -->
        <div v-if="needsContentGeneration && !generatingContent" class="bg-gradient-to-r from-primary/10 to-primary-hover/10 border border-primary/20 rounded-2xl p-6 mb-6">
          <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center flex-shrink-0">
                <svg class="w-6 h-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-text">Contenido pendiente</h3>
                <p class="text-sm text-text-secondary mt-1">
                  Las lecciones de este módulo aún no tienen contenido. Genera el contenido con IA para continuar.
                </p>
              </div>
            </div>
            <BaseButton @click="handleGenerateContent" class="flex-shrink-0">
              <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Generar contenido
            </BaseButton>
          </div>
        </div>

        <!-- Generando contenido -->
        <div v-if="generatingContent" class="bg-card border border-line rounded-2xl p-8 mb-6 text-center">
          <LoadingSpinner size="lg" class="mx-auto mb-4" />
          <p class="text-text font-medium">Generando contenido con IA...</p>
          <p class="text-sm text-text-secondary mt-1">Esto puede tomar hasta 2 minutos</p>
        </div>

        <!-- Error al generar -->
        <div v-if="generateError" class="bg-danger/10 border border-danger/20 rounded-xl p-4 mb-6 flex items-center gap-3">
          <svg class="w-5 h-5 text-danger flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm text-danger">{{ generateError }}</span>
        </div>

        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-text">Lecciones</h2>
          <BaseButton size="sm" @click="showCreateLessonModal = true">
            <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Nueva lección
          </BaseButton>
        </div>

        <!-- Lista vacía -->
        <div v-if="coursesStore.lessons.length === 0" class="bg-card border border-line rounded-2xl p-12 text-center">
          <div class="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p class="text-text font-medium mb-2">No hay lecciones</p>
          <p class="text-text-secondary text-sm mb-6">Crea la primera lección para este módulo</p>
          <BaseButton @click="showCreateLessonModal = true">
            <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Crear lección
          </BaseButton>
        </div>

        <!-- Lista de lecciones -->
        <div v-else class="space-y-3">
          <div
            v-for="(lesson, index) in coursesStore.lessons"
            :key="lesson.id"
            class="bg-card border border-line rounded-xl p-4 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5 transition-all group"
          >
            <div class="flex items-center justify-between">
              <RouterLink
                :to="`${courseRoute}/modules/${moduleId}/lessons/${lesson.id}`"
                class="flex items-center gap-4 flex-1"
              >
                <div class="w-10 h-10 bg-gradient-to-br from-primary/20 to-primary/10 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:from-primary group-hover:to-primary-hover transition-all">
                  <span class="text-sm text-primary font-bold group-hover:text-white transition-colors">{{ index + 1 }}</span>
                </div>
                <div>
                  <h3 class="font-semibold text-text group-hover:text-primary transition-colors">{{ lesson.title }}</h3>
                  <p v-if="lesson.content" class="text-sm text-text-secondary line-clamp-1">
                    {{ lesson.content.substring(0, 100) }}{{ lesson.content.length > 100 ? '...' : '' }}
                  </p>
                </div>
              </RouterLink>
              <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <RouterLink :to="`${courseRoute}/modules/${moduleId}/lessons/${lesson.id}`">
                  <BaseButton variant="ghost" size="sm">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </BaseButton>
                </RouterLink>
                <BaseButton variant="ghost" size="sm" @click.stop="openDeleteLessonConfirm(lesson.id)">
                  <svg class="w-4 h-4 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </BaseButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Modal: Crear lección -->
    <Teleport to="body">
      <div v-if="showCreateLessonModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50" @click="showCreateLessonModal = false" />
        <div class="relative bg-card border border-line rounded-2xl p-6 w-full max-w-md shadow-xl">
          <h3 class="text-lg font-bold text-text mb-4">Nueva lección</h3>
          <form @submit.prevent="handleCreateLesson" class="space-y-4">
            <BaseInput
              v-model="newLesson.title"
              label="Título"
              placeholder="Ej: Introducción al tema"
              required
            />
            <BaseTextarea
              v-model="newLesson.content"
              label="Contenido (opcional)"
              placeholder="Contenido de la lección..."
              :rows="4"
            />
            <div class="flex justify-end gap-3 pt-2">
              <BaseButton type="button" variant="secondary" @click="showCreateLessonModal = false">
                Cancelar
              </BaseButton>
              <BaseButton type="submit" :disabled="!newLesson.title.trim() || coursesStore.loading">
                {{ coursesStore.loading ? 'Creando...' : 'Crear lección' }}
              </BaseButton>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Modal: Editar módulo -->
    <Teleport to="body">
      <div v-if="showEditModuleModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50" @click="showEditModuleModal = false" />
        <div class="relative bg-card border border-line rounded-2xl p-6 w-full max-w-md shadow-xl">
          <h3 class="text-lg font-bold text-text mb-4">Editar módulo</h3>
          <form @submit.prevent="handleUpdateModule" class="space-y-4">
            <BaseInput
              v-model="editModuleData.title"
              label="Título"
              placeholder="Título del módulo"
              required
            />
            <BaseTextarea
              v-model="editModuleData.description"
              label="Descripción (opcional)"
              placeholder="Descripción del módulo..."
              :rows="3"
            />
            <div class="flex justify-end gap-3 pt-2">
              <BaseButton type="button" variant="secondary" @click="showEditModuleModal = false">
                Cancelar
              </BaseButton>
              <BaseButton type="submit" :disabled="!editModuleData.title.trim() || coursesStore.loading">
                {{ coursesStore.loading ? 'Guardando...' : 'Guardar cambios' }}
              </BaseButton>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Modal: Confirmar eliminación -->
    <Teleport to="body">
      <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50" @click="showDeleteConfirm = false" />
        <div class="relative bg-card border border-line rounded-2xl p-6 w-full max-w-sm shadow-xl">
          <div class="w-12 h-12 bg-danger/10 rounded-xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-lg font-bold text-text text-center mb-2">
            {{ lessonToDelete ? 'Eliminar lección' : 'Eliminar módulo' }}
          </h3>
          <p class="text-text-secondary text-center text-sm mb-6">
            {{ lessonToDelete 
              ? 'Esta acción eliminará la lección y todas sus preguntas.' 
              : 'Esta acción eliminará el módulo y todas sus lecciones.' 
            }}
          </p>
          <div class="flex gap-3">
            <BaseButton variant="secondary" class="flex-1" @click="showDeleteConfirm = false">
              Cancelar
            </BaseButton>
            <BaseButton 
              variant="danger" 
              class="flex-1" 
              @click="lessonToDelete ? handleDeleteLesson() : handleDeleteModule()"
              :disabled="coursesStore.loading"
            >
              {{ coursesStore.loading ? 'Eliminando...' : 'Eliminar' }}
            </BaseButton>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
