import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores'

const routes: RouteRecordRaw[] = [
  // Públicas
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue')
  },
  
  // Auth (solo invitados)
  {
    path: '/auth/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { guest: true }
  },
  {
    path: '/auth/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { guest: true }
  },
  
  // Rutas de usuario (requiere auth)
  {
    path: '/:username',
    name: 'user-dashboard',
    component: () => import('@/views/dashboard/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:username/roadmaps/new',
    name: 'roadmap-create',
    component: () => import('@/views/roadmaps/RoadmapCreateView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:username/roadmaps/:id',
    name: 'roadmap-detail',
    component: () => import('@/views/roadmaps/RoadmapDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:username/settings',
    name: 'settings',
    component: () => import('@/views/settings/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  
  // Redirects para compatibilidad
  { path: '/login', redirect: '/auth/login' },
  { path: '/register', redirect: '/auth/register' },
  
  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // Hydrate user from persisted token to avoid intermittent redirects on hard refresh.
  if (authStore.token && !authStore.user && !authStore.loading) {
    await authStore.fetchCurrentUser()
  }

  if (to.meta.requiresAuth && !authStore.token) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresAuth && authStore.token && !authStore.user) {
    next({ name: 'login' })
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next(`/${authStore.user?.username}`)
  } else {
    next()
  }
})

export default router
