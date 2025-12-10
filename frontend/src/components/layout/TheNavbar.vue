<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { useTheme } from '@/composables'

const router = useRouter()
const authStore = useAuthStore()
const { isDark, toggleTheme } = useTheme()
const mobileMenuOpen = ref(false)

const userRoutes = computed(() => {
  const username = authStore.user?.username || ''
  return {
    dashboard: `/${username}`,
    coursesNew: `/${username}/courses/new`,
    settings: `/${username}/settings`
  }
})

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <nav class="bg-card border-b border-line sticky top-0 z-50 backdrop-blur-sm bg-opacity-90">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <RouterLink to="/" class="flex items-center gap-2.5 group">
            <div class="w-9 h-9 bg-gradient-to-br from-primary to-primary-hover rounded-xl flex items-center justify-center shadow-md group-hover:shadow-lg transition-shadow">
              <span class="text-white font-bold text-lg">M</span>
            </div>
            <span class="text-xl font-bold text-text">Merq</span>
          </RouterLink>
        </div>

        <div class="hidden md:flex md:items-center md:gap-2">
          <button
            @click="toggleTheme"
            class="p-2.5 rounded-xl text-text-secondary hover:text-text hover:bg-bg-secondary transition-all"
            :title="isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'"
          >
            <svg v-if="isDark" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          </button>

          <template v-if="authStore.isAuthenticated">
            <RouterLink
              :to="userRoutes.dashboard"
              class="text-text-secondary hover:text-text px-4 py-2 text-sm font-medium transition-colors rounded-xl hover:bg-bg-secondary"
            >
              Dashboard
            </RouterLink>
            <RouterLink
              :to="userRoutes.coursesNew"
              class="bg-primary text-white hover:bg-primary-hover px-4 py-2 rounded-xl text-sm font-medium transition-all shadow-sm hover:shadow-md"
            >
              + Nuevo Curso
            </RouterLink>
            <RouterLink
              :to="userRoutes.settings"
              class="text-text-secondary hover:text-text p-2.5 rounded-xl hover:bg-bg-secondary transition-all"
              title="Configuración"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </RouterLink>
            <button
              @click="handleLogout"
              class="text-text-secondary hover:text-text px-4 py-2 text-sm font-medium transition-colors rounded-xl hover:bg-bg-secondary"
            >
              Salir
            </button>
          </template>
          <template v-else>
            <RouterLink
              to="/auth/login"
              class="text-text-secondary hover:text-text px-4 py-2 text-sm font-medium transition-colors rounded-xl hover:bg-bg-secondary"
            >
              Iniciar sesión
            </RouterLink>
            <RouterLink
              to="/auth/register"
              class="bg-primary text-white hover:bg-primary-hover px-4 py-2 rounded-xl text-sm font-medium transition-all shadow-sm hover:shadow-md"
            >
              Registrarse
            </RouterLink>
          </template>
        </div>

        <div class="flex items-center gap-2 md:hidden">
          <button
            @click="toggleTheme"
            class="p-2 rounded-xl text-text-secondary hover:text-text hover:bg-bg-secondary transition-all"
          >
            <svg v-if="isDark" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          </button>
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="text-text-secondary hover:text-text p-2 rounded-xl hover:bg-bg-secondary transition-all"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                v-if="!mobileMenuOpen"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div v-if="mobileMenuOpen" class="md:hidden border-t border-line bg-card">
      <div class="px-4 py-3 space-y-1">
        <template v-if="authStore.isAuthenticated">
          <RouterLink
            :to="userRoutes.dashboard"
            class="block text-text-secondary hover:text-text hover:bg-bg-secondary px-4 py-3 rounded-xl text-base font-medium transition-all"
            @click="mobileMenuOpen = false"
          >
            Dashboard
          </RouterLink>
          <RouterLink
            :to="userRoutes.coursesNew"
            class="block text-primary hover:bg-primary/10 px-4 py-3 rounded-xl text-base font-medium transition-all"
            @click="mobileMenuOpen = false"
          >
            + Nuevo Curso
          </RouterLink>
          <RouterLink
            :to="userRoutes.settings"
            class="block text-text-secondary hover:text-text hover:bg-bg-secondary px-4 py-3 rounded-xl text-base font-medium transition-all"
            @click="mobileMenuOpen = false"
          >
            Configuración
          </RouterLink>
          <button
            @click="handleLogout(); mobileMenuOpen = false"
            class="block w-full text-left text-text-secondary hover:text-text hover:bg-bg-secondary px-4 py-3 rounded-xl text-base font-medium transition-all"
          >
            Salir
          </button>
        </template>
        <template v-else>
          <RouterLink
            to="/auth/login"
            class="block text-text-secondary hover:text-text hover:bg-bg-secondary px-4 py-3 rounded-xl text-base font-medium transition-all"
            @click="mobileMenuOpen = false"
          >
            Iniciar sesión
          </RouterLink>
          <RouterLink
            to="/auth/register"
            class="block text-primary hover:bg-primary/10 px-4 py-3 rounded-xl text-base font-medium transition-all"
            @click="mobileMenuOpen = false"
          >
            Registrarse
          </RouterLink>
        </template>
      </div>
    </div>
  </nav>
</template>
