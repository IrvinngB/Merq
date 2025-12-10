<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { BaseButton, BaseInput, BaseCard } from '@/components/common'
import { useAuthStore } from '@/stores'
import { usersApi, authApi } from '@/api'
import type { AxiosError } from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  full_name: '',
  username: '',
  email: '',
  password: '',
  role: 'student' as const
})
const loading = ref(false)
const error = ref('')

async function handleSubmit() {
  loading.value = true
  error.value = ''

  try {
    await usersApi.create(form.value)
    const loginResponse = await authApi.login({ email: form.value.email, password: form.value.password })
    authStore.setUser(loginResponse.data.user)
    authStore.setToken(loginResponse.data.access_token)
    router.push(`/${loginResponse.data.user.username}`)
  } catch (err) {
    const axiosError = err as AxiosError<{ detail?: string }>
    error.value = axiosError.response?.data?.detail || 'Error al crear cuenta'
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
        <h1 class="text-2xl font-bold text-text">Crea tu cuenta</h1>
        <p class="text-text-secondary mt-2">Comienza a aprender de forma inteligente</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <BaseInput
          v-model="form.full_name"
          label="Nombre completo"
          placeholder="Juan Pérez"
          required
        />

        <BaseInput
          v-model="form.username"
          label="Nombre de usuario"
          placeholder="juanperez"
          required
        />
        <p class="text-xs text-text-secondary -mt-2 ml-1">3-20 caracteres, solo letras, números y guion bajo</p>

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
          placeholder="Mínimo 6 caracteres"
          required
        />

        <p v-if="error" class="text-sm text-danger text-center bg-danger/10 py-2 px-4 rounded-xl">{{ error }}</p>

        <BaseButton type="submit" :loading="loading" class="w-full">
          Crear cuenta
        </BaseButton>
      </form>

      <p class="text-center text-sm text-text-secondary mt-6">
        ¿Ya tienes cuenta?
        <RouterLink to="/auth/login" class="text-primary hover:text-primary-hover font-medium transition-colors">
          Inicia sesión
        </RouterLink>
      </p>
    </BaseCard>
  </div>
</template>
