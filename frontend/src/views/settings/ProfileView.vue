<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { BaseButton, BaseInput } from '@/components/common'
import { useAuthStore } from '@/stores'
import { usersApi } from '@/api'
import type { AxiosError } from 'axios'

const authStore = useAuthStore()

const form = ref({
  full_name: '',
  username: '',
  email: ''
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const loading = ref(false)
const passwordLoading = ref(false)
const success = ref('')
const error = ref('')
const passwordError = ref('')
const passwordSuccess = ref('')

onMounted(() => {
  if (authStore.user) {
    form.value = {
      full_name: authStore.user.full_name,
      username: authStore.user.username,
      email: authStore.user.email
    }
  }
})

async function handleUpdateProfile() {
  if (!authStore.user) return
  
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const response = await usersApi.update(authStore.user.id, {
      full_name: form.value.full_name,
      username: form.value.username,
      email: form.value.email
    })
    authStore.setUser(response.data)
    success.value = 'Perfil actualizado correctamente'
  } catch (err) {
    const axiosError = err as AxiosError<{ detail?: string }>
    error.value = axiosError.response?.data?.detail || 'Error al actualizar perfil'
  } finally {
    loading.value = false
  }
}

async function handleChangePassword() {
  if (!authStore.user) return
  
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = 'Las contraseñas no coinciden'
    return
  }

  if (passwordForm.value.new_password.length < 6) {
    passwordError.value = 'La contraseña debe tener al menos 6 caracteres'
    return
  }

  passwordLoading.value = true
  passwordError.value = ''
  passwordSuccess.value = ''

  try {
    await usersApi.update(authStore.user.id, {
      password: passwordForm.value.new_password
    })
    passwordSuccess.value = 'Contraseña actualizada correctamente'
    passwordForm.value = { current_password: '', new_password: '', confirm_password: '' }
  } catch (err) {
    const axiosError = err as AxiosError<{ detail?: string }>
    passwordError.value = axiosError.response?.data?.detail || 'Error al cambiar contraseña'
  } finally {
    passwordLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-180px)]">
    <!-- Header con gradiente -->
    <div class="bg-gradient-to-br from-primary/5 via-bg to-primary-hover/5 border-b border-line">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <div class="flex flex-col md:flex-row md:items-center gap-6">
          <div class="w-24 h-24 bg-gradient-to-br from-primary to-primary-hover rounded-3xl flex items-center justify-center shadow-xl shadow-primary/25 ring-4 ring-white dark:ring-gray-800">
            <span class="text-white font-bold text-4xl">
              {{ authStore.user?.full_name?.charAt(0)?.toUpperCase() || 'U' }}
            </span>
          </div>
          <div>
            <h1 class="text-2xl md:text-3xl font-bold text-text">{{ authStore.user?.full_name }}</h1>
            <p class="text-text-secondary mt-1">@{{ authStore.user?.username }}</p>
            <div class="flex items-center gap-3 mt-3">
              <span class="inline-flex items-center gap-1.5 text-xs font-medium text-primary bg-primary/10 px-3 py-1.5 rounded-full">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {{ authStore.user?.role === 'student' ? 'Estudiante' : authStore.user?.role === 'teacher' ? 'Profesor' : 'Admin' }}
              </span>
              <span class="inline-flex items-center gap-1.5 text-xs font-medium text-success bg-success/10 px-3 py-1.5 rounded-full">
                <span class="w-2 h-2 bg-success rounded-full animate-pulse" />
                Activo
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid lg:grid-cols-3 gap-8">
        <!-- Sidebar con info -->
        <div class="lg:col-span-1 space-y-6">
          <div class="bg-card border border-line rounded-2xl p-6">
            <h3 class="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">Información</h3>
            <div class="space-y-4">
              <div>
                <p class="text-xs text-text-secondary mb-1">Email</p>
                <p class="text-sm text-text font-medium truncate">{{ authStore.user?.email }}</p>
              </div>
              <div>
                <p class="text-xs text-text-secondary mb-1">Miembro desde</p>
                <p class="text-sm text-text font-medium">
                  {{ authStore.user?.created_at ? new Date(authStore.user.created_at).toLocaleDateString('es-ES', { year: 'numeric', month: 'long' }) : '-' }}
                </p>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-primary/10 to-primary-hover/10 border border-primary/20 rounded-2xl p-6">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 bg-primary/20 rounded-xl flex items-center justify-center">
                <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 class="font-semibold text-text">Plan Actual</h3>
            </div>
            <p class="text-2xl font-bold text-primary mb-1">Gratis</p>
            <p class="text-sm text-text-secondary mb-4">Funciones básicas incluidas</p>
            <button class="w-full bg-primary/10 hover:bg-primary/20 text-primary font-medium py-2.5 px-4 rounded-xl transition-colors text-sm">
              Actualizar plan
            </button>
          </div>
        </div>

        <!-- Main content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Perfil -->
          <div class="bg-card border border-line rounded-2xl p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
                <svg class="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <h2 class="text-lg font-bold text-text">Información personal</h2>
                <p class="text-sm text-text-secondary">Actualiza tu información de perfil</p>
              </div>
            </div>
            
            <form @submit.prevent="handleUpdateProfile" class="space-y-5">
              <div class="grid md:grid-cols-2 gap-5">
                <BaseInput
                  v-model="form.full_name"
                  label="Nombre completo"
                  placeholder="Tu nombre"
                  required
                />
                <BaseInput
                  v-model="form.username"
                  label="Nombre de usuario"
                  placeholder="username"
                  required
                />
              </div>

              <BaseInput
                v-model="form.email"
                type="email"
                label="Correo electrónico"
                placeholder="tu@email.com"
                required
              />

              <div v-if="error" class="flex items-center gap-2 text-sm text-danger bg-danger/10 py-3 px-4 rounded-xl">
                <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ error }}
              </div>
              <div v-if="success" class="flex items-center gap-2 text-sm text-success bg-success/10 py-3 px-4 rounded-xl">
                <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ success }}
              </div>

              <div class="flex justify-end pt-2">
                <BaseButton type="submit" :loading="loading">
                  <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  Guardar cambios
                </BaseButton>
              </div>
            </form>
          </div>

          <!-- Contraseña -->
          <div class="bg-card border border-line rounded-2xl p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 bg-warning/10 rounded-xl flex items-center justify-center">
                <svg class="w-5 h-5 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div>
                <h2 class="text-lg font-bold text-text">Seguridad</h2>
                <p class="text-sm text-text-secondary">Cambia tu contraseña</p>
              </div>
            </div>
            
            <form @submit.prevent="handleChangePassword" class="space-y-5">
              <div class="grid md:grid-cols-2 gap-5">
                <BaseInput
                  v-model="passwordForm.new_password"
                  type="password"
                  label="Nueva contraseña"
                  placeholder="Mínimo 6 caracteres"
                  required
                />
                <BaseInput
                  v-model="passwordForm.confirm_password"
                  type="password"
                  label="Confirmar contraseña"
                  placeholder="Repite la contraseña"
                  required
                />
              </div>

              <div v-if="passwordError" class="flex items-center gap-2 text-sm text-danger bg-danger/10 py-3 px-4 rounded-xl">
                <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ passwordError }}
              </div>
              <div v-if="passwordSuccess" class="flex items-center gap-2 text-sm text-success bg-success/10 py-3 px-4 rounded-xl">
                <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ passwordSuccess }}
              </div>

              <div class="flex justify-end pt-2">
                <BaseButton type="submit" :loading="passwordLoading" variant="secondary">
                  <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  Cambiar contraseña
                </BaseButton>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
