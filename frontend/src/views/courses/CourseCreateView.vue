<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { BaseButton, BaseInput, BaseTextarea } from '@/components/common'
import { useAuthStore } from '@/stores'
import { aiApi } from '@/api'
import type { AxiosError } from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const dashboardRoute = computed(() => `/${authStore.user?.username || ''}`)

const form = ref({
  title: '',
  content: ''
})
const selectedFile = ref<File | null>(null)
const inputMode = ref<'text' | 'file'>('file')
const loading = ref(false)
const loadingMessage = ref('')
const error = ref('')

const fileInputRef = ref<HTMLInputElement | null>(null)

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]
    const extension = file.name.split('.').pop()?.toLowerCase()
    
    if (!['pdf', 'txt'].includes(extension || '')) {
      error.value = 'Solo se permiten archivos PDF o TXT'
      return
    }
    
    if (file.size > 10 * 1024 * 1024) {
      error.value = 'El archivo no puede superar los 10MB'
      return
    }
    
    selectedFile.value = file
    error.value = ''
  }
}

function removeFile() {
  selectedFile.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleSubmit() {
  if (!authStore.user?.id) return
  if (!form.value.title.trim()) return

  const hasContent = inputMode.value === 'file' ? selectedFile.value : form.value.content.trim()
  if (!hasContent) {
    error.value = inputMode.value === 'file' 
      ? 'Selecciona un archivo PDF o TXT' 
      : 'Ingresa el contenido del curso'
    return
  }

  loading.value = true
  error.value = ''
  loadingMessage.value = 'Procesando archivo...'

  try {
    let fileToSend: File

    if (inputMode.value === 'file' && selectedFile.value) {
      fileToSend = selectedFile.value
    } else {
      const blob = new Blob([form.value.content], { type: 'text/plain' })
      fileToSend = new File([blob], 'content.txt', { type: 'text/plain' })
    }

    loadingMessage.value = 'Generando curso con IA...'
    const response = await aiApi.generateCourse(fileToSend, form.value.title, authStore.user.id)
    
    router.push(`/${authStore.user.username}/courses/${response.data.course_id}`)
  } catch (err) {
    const axiosError = err as AxiosError<{ detail?: string }>
    error.value = axiosError.response?.data?.detail || 'Error al generar el curso'
  } finally {
    loading.value = false
    loadingMessage.value = ''
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-180px)]">
    <!-- Header -->
    <div class="bg-gradient-to-br from-primary/5 via-bg to-primary-hover/5 border-b border-line">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <RouterLink
          :to="dashboardRoute"
          class="inline-flex items-center gap-2 text-text-secondary hover:text-text text-sm mb-6 transition-colors group"
        >
          <svg class="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Volver al dashboard
        </RouterLink>
        
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 bg-gradient-to-br from-primary to-primary-hover rounded-2xl flex items-center justify-center shadow-lg shadow-primary/25">
            <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </div>
          <div>
            <h1 class="text-2xl md:text-3xl font-bold text-text">Crear nuevo curso</h1>
            <p class="text-text-secondary mt-1">La IA generará módulos y lecciones automáticamente</p>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid lg:grid-cols-3 gap-8">
        <!-- Sidebar con tips -->
        <div class="lg:col-span-1 space-y-6 order-2 lg:order-1">
          <div class="bg-card border border-line rounded-2xl p-6">
            <h3 class="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">Consejos</h3>
            <div class="space-y-4">
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span class="text-primary font-bold text-sm">1</span>
                </div>
                <div>
                  <p class="text-sm font-medium text-text">Usa contenido claro</p>
                  <p class="text-xs text-text-secondary mt-0.5">Textos bien estructurados generan mejores cursos</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span class="text-primary font-bold text-sm">2</span>
                </div>
                <div>
                  <p class="text-sm font-medium text-text">Incluye ejemplos</p>
                  <p class="text-xs text-text-secondary mt-0.5">Los ejemplos ayudan a crear mejores preguntas</p>
                </div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span class="text-primary font-bold text-sm">3</span>
                </div>
                <div>
                  <p class="text-sm font-medium text-text">Revisa el resultado</p>
                  <p class="text-xs text-text-secondary mt-0.5">Podrás editar el curso después de crearlo</p>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-primary/10 to-primary-hover/10 border border-primary/20 rounded-2xl p-6">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 bg-primary/20 rounded-xl flex items-center justify-center">
                <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 class="font-semibold text-text">IA Adaptativa</h3>
            </div>
            <p class="text-sm text-text-secondary leading-relaxed">
              Nuestra IA analiza el contenido y crea un plan de estudio personalizado con dificultad progresiva.
            </p>
          </div>
        </div>

        <!-- Formulario principal -->
        <div class="lg:col-span-2 order-1 lg:order-2">
          <div class="bg-card border border-line rounded-2xl p-6 md:p-8">
            <form @submit.prevent="handleSubmit" class="space-y-6">
              <div>
                <BaseInput
                  v-model="form.title"
                  label="Nombre del curso"
                  placeholder="Ej: Cálculo Diferencial, Historia del Arte..."
                  required
                />
                <p class="text-xs text-text-secondary mt-2 ml-1">Un nombre descriptivo ayuda a identificar el curso</p>
              </div>

              <!-- Selector de modo -->
              <div>
                <label class="block text-sm font-medium text-text mb-3">Material del curso</label>
                <div class="flex gap-2 p-1 bg-bg-secondary rounded-xl">
                  <button
                    type="button"
                    @click="inputMode = 'file'"
                    :class="[
                      'flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all',
                      inputMode === 'file'
                        ? 'bg-card text-text shadow-sm'
                        : 'text-text-secondary hover:text-text'
                    ]"
                  >
                    <svg class="w-4 h-4 inline-block mr-2 -mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    Subir archivo
                  </button>
                  <button
                    type="button"
                    @click="inputMode = 'text'"
                    :class="[
                      'flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all',
                      inputMode === 'text'
                        ? 'bg-card text-text shadow-sm'
                        : 'text-text-secondary hover:text-text'
                    ]"
                  >
                    <svg class="w-4 h-4 inline-block mr-2 -mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Pegar texto
                  </button>
                </div>
              </div>

              <!-- Upload de archivo -->
              <div v-if="inputMode === 'file'">
                <input
                  ref="fileInputRef"
                  type="file"
                  accept=".pdf,.txt"
                  class="hidden"
                  @change="handleFileSelect"
                />
                
                <div
                  v-if="!selectedFile"
                  @click="triggerFileInput"
                  @dragover.prevent
                  @drop.prevent="(e) => { if (e.dataTransfer?.files[0]) { const input = { target: { files: e.dataTransfer.files } }; handleFileSelect(input as any) } }"
                  class="border-2 border-dashed border-line rounded-xl p-8 text-center cursor-pointer hover:border-primary/50 hover:bg-primary/5 transition-all"
                >
                  <div class="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg class="w-7 h-7 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <p class="text-text font-medium mb-1">Arrastra tu archivo aquí</p>
                  <p class="text-text-secondary text-sm mb-3">o haz clic para seleccionar</p>
                  <p class="text-xs text-text-secondary">PDF o TXT (máx. 10MB)</p>
                </div>

                <div
                  v-else
                  class="border border-line rounded-xl p-4 bg-bg-secondary"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                        <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <div>
                        <p class="text-sm font-medium text-text">{{ selectedFile.name }}</p>
                        <p class="text-xs text-text-secondary">{{ (selectedFile.size / 1024).toFixed(1) }} KB</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      @click="removeFile"
                      class="p-2 text-text-secondary hover:text-danger hover:bg-danger/10 rounded-lg transition-colors"
                    >
                      <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Textarea para texto -->
              <div v-else>
                <BaseTextarea
                  v-model="form.content"
                  label=""
                  placeholder="Pega aquí el texto, apuntes, temario o cualquier material que te haya dado tu profesor sobre el tema..."
                  :rows="12"
                />
                <div class="flex items-center justify-between mt-2">
                  <p class="text-xs text-text-secondary ml-1">Mínimo 100 caracteres recomendado</p>
                  <p class="text-xs text-text-secondary">{{ form.content.length }} caracteres</p>
                </div>
              </div>

              <div v-if="error" class="flex items-center gap-2 text-sm text-danger bg-danger/10 py-3 px-4 rounded-xl">
                <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ error }}
              </div>

              <!-- Loading state -->
              <div v-if="loading" class="flex items-center gap-3 text-sm text-primary bg-primary/10 py-4 px-4 rounded-xl">
                <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ loadingMessage }}</span>
              </div>

              <div class="flex flex-col sm:flex-row gap-4 pt-4">
                <BaseButton
                  type="button"
                  variant="secondary"
                  @click="router.back()"
                  class="sm:flex-1"
                  :disabled="loading"
                >
                  Cancelar
                </BaseButton>
                <BaseButton
                  type="submit"
                  :disabled="!form.title || loading || (inputMode === 'file' ? !selectedFile : !form.content)"
                  class="sm:flex-1 group"
                >
                  <svg v-if="!loading" class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  {{ loading ? 'Generando...' : 'Generar curso con IA' }}
                  <svg v-if="!loading" class="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </BaseButton>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
