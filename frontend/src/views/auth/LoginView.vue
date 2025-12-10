<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { BaseButton, BaseInput, BaseCard } from '@/components/common'
import { useAuthStore } from '@/stores'
import { authApi } from '@/api'
import type { AxiosError } from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleSubmit() {
  loading.value = true
  error.value = ''

  try {
    const response = await authApi.login(form.value)
    authStore.setUser(response.data.user)
    authStore.setToken(response.data.access_token)
    router.push(`/${response.data.user.username}`)
  } catch (err) {
    const axiosError = err as AxiosError<{ detail?: string }>
    error.value = axiosError.response?.data?.detail || 'Error al iniciar sesión'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-180px)] flex items-center justify-center py-12 px-4">
    <BaseCard class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-14 h-14 bg-gradient-to-br from-primary to-primary-hover rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
          <span class="text-white font-bold text-2xl">M</span>
        </div>
        <h1 class="text-2xl font-bold text-text">Bienvenido de vuelta</h1>
        <p class="text-text-secondary mt-2">Ingresa a tu cuenta para continuar</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-5">
        <BaseInput
          v-model="form.email"
          type="email"
          label="Correo electrónico"
          placeholder="tu@email.com"
          required
        />

        <BaseInput
          v-model="form.password"
          type="password"
          label="Contraseña"
          placeholder="••••••••"
          required
        />

        <p v-if="error" class="text-sm text-danger text-center bg-danger/10 py-2 px-4 rounded-xl">{{ error }}</p>

        <BaseButton type="submit" :loading="loading" class="w-full">
          Iniciar sesión
        </BaseButton>
      </form>

      <p class="text-center text-sm text-text-secondary mt-6">
        ¿No tienes cuenta?
        <RouterLink to="/auth/register" class="text-primary hover:text-primary-hover font-medium transition-colors">
          Regístrate
        </RouterLink>
      </p>
    </BaseCard>
  </div>
</template>
