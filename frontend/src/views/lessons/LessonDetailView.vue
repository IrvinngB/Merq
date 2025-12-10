<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { BaseButton, BaseInput, BaseTextarea, LoadingSpinner, MarkdownRenderer } from '@/components/common'
import { useCoursesStore, useAuthStore } from '@/stores'
import type { QuestionCreate } from '@/types'

const route = useRoute()
const router = useRouter()
const coursesStore = useCoursesStore()
const authStore = useAuthStore()

const courseId = computed(() => Number(route.params.id))
const moduleId = computed(() => Number(route.params.moduleId))
const lessonId = computed(() => Number(route.params.lessonId))
const dashboardRoute = computed(() => `/${authStore.user?.username || ''}`)
const courseRoute = computed(() => `/${authStore.user?.username}/courses/${courseId.value}`)
const moduleRoute = computed(() => `${courseRoute.value}/modules/${moduleId.value}`)

const showEditLessonModal = ref(false)
const showDeleteConfirm = ref(false)
const showCreateQuestionModal = ref(false)
const questionToDelete = ref<number | null>(null)

const editLessonData = ref({ title: '', content: '' })

const newQuestion = ref<QuestionCreate>({
  text: '',
  question_type: 'multiple_choice',
  difficulty: 'medium',
  options: [
    { text: '', is_correct: true },
    { text: '', is_correct: false },
    { text: '', is_correct: false },
    { text: '', is_correct: false }
  ]
})

const questionTypes = [
  { value: 'multiple_choice', label: 'Opción múltiple' },
  { value: 'true_false', label: 'Verdadero/Falso' },
  { value: 'open', label: 'Respuesta abierta' }
] as const

const difficultyLevels = [
  { value: 'easy', label: 'Fácil', color: 'text-success' },
  { value: 'medium', label: 'Medio', color: 'text-warning' },
  { value: 'hard', label: 'Difícil', color: 'text-danger' }
] as const

onMounted(async () => {
  await Promise.all([
    coursesStore.fetchCourse(courseId.value),
    coursesStore.fetchModule(courseId.value, moduleId.value),
    coursesStore.fetchLesson(moduleId.value, lessonId.value),
    coursesStore.fetchQuestions(lessonId.value)
  ])
  if (coursesStore.currentLesson) {
    editLessonData.value = {
      title: coursesStore.currentLesson.title,
      content: coursesStore.currentLesson.content || ''
    }
  }
})

onUnmounted(() => {
  coursesStore.clearLesson()
})

function resetNewQuestion() {
  newQuestion.value = {
    text: '',
    question_type: 'multiple_choice',
    difficulty: 'medium',
    options: [
      { text: '', is_correct: true },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false }
    ]
  }
}

function handleQuestionTypeChange() {
  if (newQuestion.value.question_type === 'true_false') {
    newQuestion.value.options = [
      { text: 'Verdadero', is_correct: true },
      { text: 'Falso', is_correct: false }
    ]
  } else if (newQuestion.value.question_type === 'open') {
    newQuestion.value.options = []
  } else {
    newQuestion.value.options = [
      { text: '', is_correct: true },
      { text: '', is_correct: false },
      { text: '', is_correct: false },
      { text: '', is_correct: false }
    ]
  }
}

function setCorrectOption(index: number) {
  newQuestion.value.options?.forEach((opt, i) => {
    opt.is_correct = i === index
  })
}

async function handleUpdateLesson() {
  if (!editLessonData.value.title.trim()) return
  try {
    await coursesStore.updateLesson(moduleId.value, lessonId.value, editLessonData.value)
    showEditLessonModal.value = false
  } catch {
    // error manejado en store
  }
}

async function handleDeleteLesson() {
  try {
    await coursesStore.deleteLesson(moduleId.value, lessonId.value)
    router.push(moduleRoute.value)
  } catch {
    // error manejado en store
  }
}

async function handleCreateQuestion() {
  if (!newQuestion.value.text.trim()) return
  
  const hasValidOptions = newQuestion.value.question_type === 'open' || 
    (newQuestion.value.options?.some(o => o.text.trim()) && 
     newQuestion.value.options?.some(o => o.is_correct))
  
  if (!hasValidOptions && newQuestion.value.question_type !== 'open') return

  const questionData: QuestionCreate = {
    ...newQuestion.value,
    options: newQuestion.value.question_type === 'open' 
      ? [] 
      : newQuestion.value.options?.filter(o => o.text.trim())
  }

  try {
    await coursesStore.createQuestion(lessonId.value, questionData)
    showCreateQuestionModal.value = false
    resetNewQuestion()
  } catch {
    // error manejado en store
  }
}

async function handleDeleteQuestion() {
  if (!questionToDelete.value) return
  try {
    await coursesStore.deleteQuestion(lessonId.value, questionToDelete.value)
    questionToDelete.value = null
    showDeleteConfirm.value = false
  } catch {
    // error manejado en store
  }
}

function openDeleteQuestionConfirm(questionId: number) {
  questionToDelete.value = questionId
  showDeleteConfirm.value = true
}

function getDifficultyLabel(difficulty: string) {
  return difficultyLevels.find(d => d.value === difficulty)?.label || difficulty
}

function getDifficultyColor(difficulty: string) {
  return difficultyLevels.find(d => d.value === difficulty)?.color || 'text-text-secondary'
}

function getQuestionTypeLabel(type: string) {
  return questionTypes.find(t => t.value === type)?.label || type
}
</script>

<template>
  <div class="min-h-[calc(100vh-180px)]">
    <!-- Loading -->
    <div v-if="coursesStore.loading && !coursesStore.currentLesson" class="flex items-center justify-center py-24">
      <LoadingSpinner size="lg" />
    </div>

    <!-- Error -->
    <div v-else-if="coursesStore.error && !coursesStore.currentLesson" class="max-w-md mx-auto text-center py-24 px-4">
      <div class="w-20 h-20 bg-danger/10 rounded-3xl flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h2 class="text-xl font-bold text-text mb-2">Error al cargar la lección</h2>
      <p class="text-text-secondary mb-6">{{ coursesStore.error }}</p>
      <RouterLink :to="moduleRoute">
        <BaseButton variant="secondary">Volver al módulo</BaseButton>
      </RouterLink>
    </div>

    <!-- Content -->
    <template v-else-if="coursesStore.currentLesson">
      <!-- Header -->
      <div class="bg-gradient-to-br from-primary/5 via-bg to-primary-hover/5 border-b border-line">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <!-- Breadcrumb -->
          <nav class="flex items-center gap-2 text-sm text-text-secondary mb-6 flex-wrap">
            <RouterLink :to="dashboardRoute" class="hover:text-text transition-colors">Dashboard</RouterLink>
            <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <RouterLink :to="courseRoute" class="hover:text-text transition-colors">
              {{ coursesStore.currentCourse?.title || 'Curso' }}
            </RouterLink>
            <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <RouterLink :to="moduleRoute" class="hover:text-text transition-colors">
              {{ coursesStore.currentModule?.title || 'Módulo' }}
            </RouterLink>
            <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span class="text-text">{{ coursesStore.currentLesson.title }}</span>
          </nav>

          <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
            <div class="flex items-start gap-5">
              <div class="w-14 h-14 bg-gradient-to-br from-primary to-primary-hover rounded-2xl flex items-center justify-center shadow-lg shadow-primary/25 flex-shrink-0">
                <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h1 class="text-2xl md:text-3xl font-bold text-text">{{ coursesStore.currentLesson.title }}</h1>
                <p class="text-text-secondary text-sm mt-1">
                  {{ coursesStore.questions.length }} pregunta(s)
                </p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <BaseButton variant="secondary" size="sm" @click="showEditLessonModal = true">
                <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Editar
              </BaseButton>
              <BaseButton variant="danger" size="sm" @click="showDeleteConfirm = true; questionToDelete = null">
                <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Eliminar
              </BaseButton>
            </div>
          </div>
        </div>
      </div>

      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid lg:grid-cols-3 gap-8">
          <!-- Contenido de la lección -->
          <div class="lg:col-span-2 space-y-8">
            <!-- Contenido -->
            <div v-if="coursesStore.currentLesson.content" class="bg-card border border-line rounded-2xl p-6">
              <h2 class="text-lg font-bold text-text mb-4">Contenido</h2>
              <MarkdownRenderer :content="coursesStore.currentLesson.content" />
            </div>

            <!-- Preguntas -->
            <div>
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-bold text-text">Preguntas</h2>
                <BaseButton size="sm" @click="showCreateQuestionModal = true">
                  <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Nueva pregunta
                </BaseButton>
              </div>

              <!-- Lista vacía -->
              <div v-if="coursesStore.questions.length === 0" class="bg-card border border-line rounded-2xl p-12 text-center">
                <div class="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p class="text-text font-medium mb-2">No hay preguntas</p>
                <p class="text-text-secondary text-sm mb-6">Crea preguntas para evaluar esta lección</p>
                <BaseButton @click="showCreateQuestionModal = true">
                  <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Crear pregunta
                </BaseButton>
              </div>

              <!-- Lista de preguntas -->
              <div v-else class="space-y-4">
                <div
                  v-for="(question, index) in coursesStore.questions"
                  :key="question.id"
                  class="bg-card border border-line rounded-xl p-5 group"
                >
                  <div class="flex items-start justify-between gap-4">
                    <div class="flex-1">
                      <div class="flex items-center gap-3 mb-2">
                        <span class="text-xs font-medium text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                          {{ index + 1 }}
                        </span>
                        <span class="text-xs text-text-secondary">
                          {{ getQuestionTypeLabel(question.question_type) }}
                        </span>
                        <span :class="['text-xs font-medium', getDifficultyColor(question.difficulty)]">
                          {{ getDifficultyLabel(question.difficulty) }}
                        </span>
                      </div>
                      <p class="text-text font-medium">{{ question.text }}</p>
                      
                      <!-- Opciones -->
                      <div v-if="question.options && question.options.length > 0" class="mt-3 space-y-2">
                        <div
                          v-for="option in question.options"
                          :key="option.id"
                          :class="[
                            'flex items-center gap-2 text-sm px-3 py-2 rounded-lg',
                            option.is_correct 
                              ? 'bg-success/10 text-success border border-success/20' 
                              : 'bg-bg-secondary text-text-secondary'
                          ]"
                        >
                          <svg v-if="option.is_correct" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                          </svg>
                          <span class="w-4 h-4 flex-shrink-0 rounded-full border border-current" v-else />
                          {{ option.text }}
                        </div>
                      </div>
                    </div>
                    <BaseButton 
                      variant="ghost" 
                      size="sm" 
                      class="opacity-0 group-hover:opacity-100 transition-opacity"
                      @click="openDeleteQuestionConfirm(question.id)"
                    >
                      <svg class="w-4 h-4 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </BaseButton>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="space-y-6">
            <div class="bg-card border border-line rounded-2xl p-6">
              <h3 class="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">Resumen</h3>
              <div class="space-y-4">
                <div class="flex items-center justify-between">
                  <span class="text-text-secondary">Total preguntas</span>
                  <span class="text-text font-bold">{{ coursesStore.questions.length }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-text-secondary">Fáciles</span>
                  <span class="text-success font-medium">
                    {{ coursesStore.questions.filter(q => q.difficulty === 'easy').length }}
                  </span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-text-secondary">Medias</span>
                  <span class="text-warning font-medium">
                    {{ coursesStore.questions.filter(q => q.difficulty === 'medium').length }}
                  </span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-text-secondary">Difíciles</span>
                  <span class="text-danger font-medium">
                    {{ coursesStore.questions.filter(q => q.difficulty === 'hard').length }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Modal: Editar lección -->
    <Teleport to="body">
      <div v-if="showEditLessonModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50" @click="showEditLessonModal = false" />
        <div class="relative bg-card border border-line rounded-2xl p-6 w-full max-w-lg shadow-xl">
          <h3 class="text-lg font-bold text-text mb-4">Editar lección</h3>
          <form @submit.prevent="handleUpdateLesson" class="space-y-4">
            <BaseInput
              v-model="editLessonData.title"
              label="Título"
              placeholder="Título de la lección"
              required
            />
            <BaseTextarea
              v-model="editLessonData.content"
              label="Contenido"
              placeholder="Contenido de la lección..."
              :rows="6"
            />
            <div class="flex justify-end gap-3 pt-2">
              <BaseButton type="button" variant="secondary" @click="showEditLessonModal = false">
                Cancelar
              </BaseButton>
              <BaseButton type="submit" :disabled="!editLessonData.title.trim() || coursesStore.loading">
                {{ coursesStore.loading ? 'Guardando...' : 'Guardar cambios' }}
              </BaseButton>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Modal: Crear pregunta -->
    <Teleport to="body">
      <div v-if="showCreateQuestionModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50" @click="showCreateQuestionModal = false" />
        <div class="relative bg-card border border-line rounded-2xl p-6 w-full max-w-lg shadow-xl max-h-[90vh] overflow-y-auto">
          <h3 class="text-lg font-bold text-text mb-4">Nueva pregunta</h3>
          <form @submit.prevent="handleCreateQuestion" class="space-y-4">
            <BaseTextarea
              v-model="newQuestion.text"
              label="Pregunta"
              placeholder="Escribe la pregunta..."
              :rows="3"
              required
            />
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-text mb-2">Tipo</label>
                <select
                  v-model="newQuestion.question_type"
                  @change="handleQuestionTypeChange"
                  class="w-full rounded-xl border border-line bg-bg-secondary px-4 py-3 text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                >
                  <option v-for="type in questionTypes" :key="type.value" :value="type.value">
                    {{ type.label }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-text mb-2">Dificultad</label>
                <select
                  v-model="newQuestion.difficulty"
                  class="w-full rounded-xl border border-line bg-bg-secondary px-4 py-3 text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                >
                  <option v-for="level in difficultyLevels" :key="level.value" :value="level.value">
                    {{ level.label }}
                  </option>
                </select>
              </div>
            </div>

            <!-- Opciones para multiple choice -->
            <div v-if="newQuestion.question_type === 'multiple_choice'" class="space-y-3">
              <label class="block text-sm font-medium text-text">Opciones (marca la correcta)</label>
              <div
                v-for="(option, index) in newQuestion.options"
                :key="index"
                class="flex items-center gap-3"
              >
                <button
                  type="button"
                  @click="setCorrectOption(index)"
                  :class="[
                    'w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors',
                    option.is_correct 
                      ? 'border-success bg-success' 
                      : 'border-line hover:border-primary'
                  ]"
                >
                  <svg v-if="option.is_correct" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
                <input
                  v-model="option.text"
                  type="text"
                  :placeholder="`Opción ${index + 1}`"
                  class="flex-1 rounded-lg border border-line bg-bg-secondary px-3 py-2 text-sm text-text placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                />
              </div>
            </div>

            <!-- Opciones para true/false -->
            <div v-if="newQuestion.question_type === 'true_false'" class="space-y-3">
              <label class="block text-sm font-medium text-text">Respuesta correcta</label>
              <div class="flex gap-4">
                <button
                  type="button"
                  @click="setCorrectOption(0)"
                  :class="[
                    'flex-1 py-3 rounded-xl border-2 font-medium transition-colors',
                    newQuestion.options?.[0]?.is_correct
                      ? 'border-success bg-success/10 text-success'
                      : 'border-line text-text-secondary hover:border-primary'
                  ]"
                >
                  Verdadero
                </button>
                <button
                  type="button"
                  @click="setCorrectOption(1)"
                  :class="[
                    'flex-1 py-3 rounded-xl border-2 font-medium transition-colors',
                    newQuestion.options?.[1]?.is_correct
                      ? 'border-success bg-success/10 text-success'
                      : 'border-line text-text-secondary hover:border-primary'
                  ]"
                >
                  Falso
                </button>
              </div>
            </div>

            <div class="flex justify-end gap-3 pt-2">
              <BaseButton type="button" variant="secondary" @click="showCreateQuestionModal = false; resetNewQuestion()">
                Cancelar
              </BaseButton>
              <BaseButton type="submit" :disabled="!newQuestion.text.trim() || coursesStore.loading">
                {{ coursesStore.loading ? 'Creando...' : 'Crear pregunta' }}
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
            {{ questionToDelete ? 'Eliminar pregunta' : 'Eliminar lección' }}
          </h3>
          <p class="text-text-secondary text-center text-sm mb-6">
            {{ questionToDelete 
              ? 'Esta acción eliminará la pregunta permanentemente.' 
              : 'Esta acción eliminará la lección y todas sus preguntas.' 
            }}
          </p>
          <div class="flex gap-3">
            <BaseButton variant="secondary" class="flex-1" @click="showDeleteConfirm = false">
              Cancelar
            </BaseButton>
            <BaseButton 
              variant="danger" 
              class="flex-1" 
              @click="questionToDelete ? handleDeleteQuestion() : handleDeleteLesson()"
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
