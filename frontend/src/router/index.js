import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: () => import('../pages/LandingPage.vue'),
  },
  {
    path: '/auth/login',
    name: 'login',
    component: () => import('../pages/auth/LoginPage.vue'),
  },
  {
    path: '/auth/register',
    name: 'register',
    component: () => import('../pages/auth/RegisterPage.vue'),
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../pages/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../pages/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/interviews/create',
    name: 'interview-create',
    component: () => import('../pages/InterviewCreatePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/interviews/:id',
    name: 'interview',
    component: () => import('../pages/InterviewPage.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  try {
    const authStore = useAuthStore()
    
    // Check if route requires authentication
    if (to.meta.requiresAuth) {
      const hasToken = authStore.isAuthenticated || !!localStorage.getItem('accessToken')
      
      if (!hasToken) {
        next({ name: 'login', query: { redirect: to.fullPath } })
        return
      }
    }
    
    next()
  } catch (error) {
    next()
  }
})

export default router

