<script setup lang="ts">
import { ref, computed, watch } from 'vue'
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
const jsonContent = ref('')
const inputMode = ref<'file' | 'text' | 'json'>('file')
const loading = ref(false)
const error = ref<string | null>(null)
const jsonError = ref<string | null>(null)

// Limpiar error cuando cambia el modo
watch(inputMode, () => {
  error.value = null
})

// Template del prompt para copiar
const promptTemplate = `Eres un experto en diseño de rutas de aprendizaje. Analiza el contenido del documento y crea un roadmap educativo.

RESPONDE ÚNICAMENTE CON JSON VÁLIDO. Sin texto adicional.

Formato JSON:
{
  "description": "Descripción breve del roadmap",
  "nodes": [
    {"title": "Tema", "description": "Qué aprenderás", "level": "beginner", "order": 0, "prerequisites": []}
  ]
}

ESTRUCTURA:
- beginner (4-6 nodos): Fundamentos básicos. prerequisites: []
- intermediate (4-6 nodos): Técnicas intermedias. prerequisites: [1-2 índices beginner]
- advanced (3-5 nodos): Especialización. prerequisites: [1-2 índices intermediate]

REGLAS:
1. Total: 12-17 nodos
2. Títulos: 2-5 palabras
3. level: "beginner", "intermediate" o "advanced" (minúsculas)
4. order: 0, 1, 2, 3... secuencial
5. prerequisites: array de números "order" de nodos previos

JSON:`

function copyPrompt() {
  navigator.clipboard.writeText(promptTemplate)
}

const isValid = computed(() => {
  const hasTitle = !!title.value.trim()
  const fileValid = inputMode.value !== 'file' || !!file.value
  const textValid = inputMode.value !== 'text' || textContent.value.trim().length >= 100
  const jsonValid = inputMode.value !== 'json' || (!!jsonContent.value.trim() && !jsonError.value)
  
  return hasTitle && fileValid && textValid && jsonValid
})

// Validar JSON mientras escribe
function validateJson() {
  jsonError.value = null
  if (!jsonContent.value.trim()) return
  
  try {
    const parsed = JSON.parse(jsonContent.value)
    
    if (!parsed.nodes || !Array.isArray(parsed.nodes)) {
      jsonError.value = 'El JSON debe tener un array "nodes"'
      return
    }
    
    if (parsed.nodes.length === 0) {
      jsonError.value = 'Debe haber al menos un nodo'
      return
    }
    
    const validLevels = ['beginner', 'intermediate', 'advanced']
    for (const node of parsed.nodes) {
      if (!node.title) {
        jsonError.value = 'Todos los nodos deben tener "title"'
        return
      }
      if (node.level && !validLevels.includes(node.level)) {
        jsonError.value = `Nivel inválido "${node.level}". Use: beginner, intermediate, advanced`
        return
      }
    }
    // JSON válido - asegurar que no hay error
    jsonError.value = null
  } catch {
    jsonError.value = 'JSON inválido - verifica la sintaxis'
  }
}

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

  // Validación extra para JSON
  if (inputMode.value === 'json' && jsonError.value) return

  loading.value = true
  error.value = null

  try {
    if (inputMode.value === 'json') {
      // Importar desde JSON
      const parsed = JSON.parse(jsonContent.value)
      const response = await aiApi.importRoadmap(title.value, authStore.user.id, {
        description: parsed.description,
        nodes: parsed.nodes.map((n: { title: string; description?: string; level?: string; order?: number; prerequisites?: number[] }) => ({
          title: n.title,
          description: n.description || null,
          level: n.level || 'beginner',
          order: n.order ?? 0,
          prerequisites: n.prerequisites || []
        }))
      })
      router.push(`${dashboardRoute.value}/roadmaps/${response.data.roadmap_id}`)
    } else {
      // Generar con IA local
      let uploadFile: File

      if (inputMode.value === 'text') {
        const blob = new Blob([textContent.value], { type: 'text/plain' })
        uploadFile = new File([blob], 'content.txt', { type: 'text/plain' })
      } else {
        uploadFile = file.value!
      }

      const response = await aiApi.generateRoadmap(uploadFile, title.value, authStore.user.id)
      router.push(`${dashboardRoute.value}/roadmaps/${response.data.roadmap_id}`)
    }
  } catch (err: unknown) {
    console.error('Error creating roadmap:', err)
    const axiosError = err as { response?: { data?: { detail?: string } }; message?: string }
    error.value = axiosError.response?.data?.detail || axiosError.message || 'Error al crear el roadmap'
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
        <p class="text-text-secondary">Sube un PDF, pega texto o importa un JSON generado con IA externa</p>
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
            <button
              @click="inputMode = 'json'"
              class="flex-1 py-3 px-4 rounded-xl border-2 transition-all text-sm font-medium"
              :class="inputMode === 'json' 
                ? 'border-amber-500 bg-amber-500/10 text-amber-500' 
                : 'border-line text-text-secondary hover:border-text-secondary'"
            >
              <svg class="w-5 h-5 mx-auto mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Importar JSON
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
        <div v-else-if="inputMode === 'text'" class="mb-6">
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

        <!-- JSON Import -->
        <div v-else-if="inputMode === 'json'" class="mb-6 space-y-4">
          <!-- Info Box -->
          <div class="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
            <div class="flex items-start gap-3">
              <svg class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="flex-1">
                <p class="text-sm text-amber-200 font-medium mb-1">¿Tienes un PDF muy grande?</p>
                <p class="text-xs text-amber-200/70 mb-3">
                  Usa Claude, GPT o Gemini para generar el JSON del roadmap y pégalo aquí.
                </p>
                <button
                  type="button"
                  @click="copyPrompt"
                  class="inline-flex items-center gap-2 text-xs font-medium text-amber-500 hover:text-amber-400 transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copiar prompt para IA externa
                </button>
              </div>
            </div>
          </div>

          <!-- JSON Textarea -->
          <div>
            <label class="block text-sm font-medium text-text mb-2">JSON del roadmap</label>
            <textarea
              v-model="jsonContent"
              @input="validateJson"
              placeholder='{
  "description": "Descripción del roadmap",
  "nodes": [
    {"title": "Tema 1", "description": "...", "level": "beginner", "order": 0, "prerequisites": []},
    {"title": "Tema 2", "description": "...", "level": "intermediate", "order": 1, "prerequisites": [0]}
  ]
}'
              class="w-full h-64 px-4 py-3 bg-bg border rounded-xl text-text placeholder-text-secondary focus:outline-none focus:ring-2 resize-none font-mono text-sm"
              :class="jsonError 
                ? 'border-danger focus:ring-danger/50 focus:border-danger' 
                : 'border-line focus:ring-primary/50 focus:border-primary'"
              :disabled="loading"
            />
            <div class="flex items-center justify-between mt-2">
              <p v-if="jsonError" class="text-xs text-danger flex items-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ jsonError }}
              </p>
              <p v-else-if="jsonContent.trim()" class="text-xs text-success flex items-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                JSON válido
              </p>
              <p v-else class="text-xs text-text-secondary">
                Pega el JSON generado por Claude, GPT o Gemini
              </p>
            </div>
          </div>

          <!-- Example Structure -->
          <details class="group">
            <summary class="text-xs text-text-secondary cursor-pointer hover:text-text flex items-center gap-1">
              <svg class="w-3.5 h-3.5 transition-transform group-open:rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              Ver estructura esperada
            </summary>
            <pre class="mt-2 p-3 bg-bg rounded-lg text-xs text-text-secondary overflow-x-auto font-mono">{{ `{
  "description": "Descripción breve",
  "nodes": [
    {
      "title": "Tema",
      "description": "Qué aprenderás",
      "level": "beginner|intermediate|advanced",
      "order": 0,
      "prerequisites": []
    }
  ]
}` }}</pre>
          </details>
        </div>

        <!-- Error -->
        <div v-if="error" class="mb-6 p-4 bg-danger/10 border border-danger/20 rounded-xl text-danger text-sm">
          {{ error }}
        </div>

        <!-- Submit -->
        <BaseButton
          class="w-full"
          size="lg"
          :disabled="!isValid || loading || (inputMode === 'json' && !!jsonError)"
          :loading="loading"
          @click="handleSubmit"
        >
          <svg v-if="!loading && inputMode !== 'json'" class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <svg v-if="!loading && inputMode === 'json'" class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          {{ loading 
            ? (inputMode === 'json' ? 'Importando...' : 'Generando roadmap...') 
            : (inputMode === 'json' ? 'Importar roadmap' : 'Generar roadmap con IA') 
          }}
        </BaseButton>

        <p v-if="loading && inputMode !== 'json'" class="text-center text-text-secondary text-sm mt-4">
          Esto puede tomar hasta 2 minutos dependiendo del contenido...
        </p>
      </div>
    </div>
  </div>
</template>
