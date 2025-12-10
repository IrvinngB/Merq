<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { BaseButton, BaseInput } from '@/components/common'
import { useAuthStore } from '@/stores'
import { aiApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const dashboardRoute = computed(() => `/${authStore.user?.username || ''}`)

const title = ref('')
const file = ref<File | null>(null)
const textContent = ref('')
const inputMode = ref<'file' | 'text'>('file')
const loading = ref(false)
const error = ref<string | null>(null)

const isValid = computed(() => {
  if (!title.value.trim()) return false
  if (inputMode.value === 'file' && !file.value) return false
  if (inputMode.value === 'text' && textContent.value.trim().length < 100) return false
  return true
})

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    file.value = target.files[0]
  }
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    const droppedFile = event.dataTransfer.files[0]
    const ext = droppedFile.name.split('.').pop()?.toLowerCase()
    if (ext === 'pdf' || ext === 'txt') {
      file.value = droppedFile
    }
  }
}

async function handleSubmit() {
  if (!isValid.value || !authStore.user?.id) return

  loading.value = true
  error.value = null

  try {
    let uploadFile: File

    if (inputMode.value === 'text') {
      const blob = new Blob([textContent.value], { type: 'text/plain' })
      uploadFile = new File([blob], 'content.txt', { type: 'text/plain' })
    } else {
      uploadFile = file.value!
    }

    const response = await aiApi.generateRoadmap(uploadFile, title.value, authStore.user.id)
    router.push(`${dashboardRoute.value}/roadmaps/${response.data.roadmap_id}`)
  } catch (err: unknown) {
    const axiosError = err as { response?: { data?: { detail?: string } } }
    error.value = axiosError.response?.data?.detail || 'Error al generar el roadmap'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-180px)]">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <RouterLink
        :to="dashboardRoute"
        class="inline-flex items-center gap-2 text-text-secondary hover:text-text text-sm mb-6 transition-colors group"
      >
        <svg class="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Volver al dashboard
      </RouterLink>

      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-gradient-to-br from-primary to-primary-hover rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary/25">
          <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
        </div>
        <h1 class="text-2xl md:text-3xl font-bold text-text mb-2">Crear nuevo roadmap</h1>
        <p class="text-text-secondary">Sube un PDF o pega texto para generar un roadmap de aprendizaje</p>
      </div>

      <!-- Form -->
      <div class="bg-card border border-line rounded-2xl p-6 md:p-8">
        <!-- Title -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-text mb-2">Título del roadmap</label>
          <BaseInput
            v-model="title"
            placeholder="Ej: Fundamentos de Python, Machine Learning Básico..."
            :disabled="loading"
          />
        </div>

        <!-- Input Mode Toggle -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-text mb-3">Fuente del contenido</label>
          <div class="flex gap-2">
            <button
              @click="inputMode = 'file'"
              class="flex-1 py-3 px-4 rounded-xl border-2 transition-all text-sm font-medium"
              :class="inputMode === 'file' 
                ? 'border-primary bg-primary/10 text-primary' 
                : 'border-line text-text-secondary hover:border-text-secondary'"
            >
              <svg class="w-5 h-5 mx-auto mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Subir archivo
            </button>
            <button
              @click="inputMode = 'text'"
              class="flex-1 py-3 px-4 rounded-xl border-2 transition-all text-sm font-medium"
              :class="inputMode === 'text' 
                ? 'border-primary bg-primary/10 text-primary' 
                : 'border-line text-text-secondary hover:border-text-secondary'"
            >
              <svg class="w-5 h-5 mx-auto mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Pegar texto
            </button>
          </div>
        </div>

        <!-- File Upload -->
        <div v-if="inputMode === 'file'" class="mb-6">
          <div
            class="border-2 border-dashed border-line rounded-xl p-8 text-center transition-colors hover:border-primary/50"
            :class="{ 'border-primary bg-primary/5': file }"
            @dragover.prevent
            @drop="handleDrop"
          >
            <input
              type="file"
              accept=".pdf,.txt"
              class="hidden"
              id="file-upload"
              @change="handleFileChange"
              :disabled="loading"
            />
            <label for="file-upload" class="cursor-pointer">
              <div v-if="!file" class="space-y-3">
                <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mx-auto">
                  <svg class="w-6 h-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div>
                  <p class="text-text font-medium">Arrastra un archivo o haz clic para seleccionar</p>
                  <p class="text-text-secondary text-sm mt-1">PDF o TXT (máx. 10MB)</p>
                </div>
              </div>
              <div v-else class="flex items-center justify-center gap-3">
                <div class="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div class="text-left">
                  <p class="text-text font-medium">{{ file.name }}</p>
                  <p class="text-text-secondary text-sm">{{ (file.size / 1024).toFixed(1) }} KB</p>
                </div>
                <button
                  type="button"
                  @click.stop="file = null"
                  class="p-1.5 rounded-lg text-text-secondary hover:text-danger hover:bg-danger/10 transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </label>
          </div>
        </div>

        <!-- Text Input -->
        <div v-else class="mb-6">
          <textarea
            v-model="textContent"
            placeholder="Pega aquí el contenido del que quieres generar el roadmap (mínimo 100 caracteres)..."
            class="w-full h-64 px-4 py-3 bg-bg border border-line rounded-xl text-text placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary resize-none"
            :disabled="loading"
          />
          <p class="text-xs text-text-secondary mt-2">
            {{ textContent.length }} caracteres (mínimo 100)
          </p>
        </div>

        <!-- Error -->
        <div v-if="error" class="mb-6 p-4 bg-danger/10 border border-danger/20 rounded-xl text-danger text-sm">
          {{ error }}
        </div>

        <!-- Submit -->
        <BaseButton
          class="w-full"
          size="lg"
          :disabled="!isValid || loading"
          :loading="loading"
          @click="handleSubmit"
        >
          <svg v-if="!loading" class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          {{ loading ? 'Generando roadmap...' : 'Generar roadmap con IA' }}
        </BaseButton>

        <p v-if="loading" class="text-center text-text-secondary text-sm mt-4">
          Esto puede tomar hasta 2 minutos dependiendo del contenido...
        </p>
      </div>
    </div>
  </div>
</template>
