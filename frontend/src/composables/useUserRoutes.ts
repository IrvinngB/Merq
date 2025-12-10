import { computed } from 'vue'
import { useAuthStore } from '@/stores'

export function useUserRoutes() {
  const authStore = useAuthStore()

  const username = computed(() => authStore.user?.username || '')

  const routes = computed(() => ({
    dashboard: `/${username.value}`,
    coursesNew: `/${username.value}/courses/new`,
    course: (id: number | string) => `/${username.value}/courses/${id}`,
    settings: `/${username.value}/settings`
  }))

  return {
    username,
    routes
  }
}
