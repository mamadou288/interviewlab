<template>
  <nav class="bg-white border-b border-gray-200 sticky top-0 z-50 backdrop-blur-sm bg-white/95">
    <div class="container-custom">
      <div class="flex justify-between items-center h-16 lg:h-20">
        <!-- Logo/Brand -->
        <RouterLink to="/dashboard" class="flex items-center space-x-2 group">
          <div class="w-8 h-8 bg-gray-900 rounded-lg flex items-center justify-center group-hover:bg-gray-800 transition-colors">
            <span class="text-white font-bold text-sm">IL</span>
          </div>
          <span class="text-xl font-bold text-gray-900 hidden sm:block">InterviewLab</span>
        </RouterLink>

            <!-- Navigation Links -->
            <div class="flex items-center space-x-2">
              <RouterLink
                to="/dashboard"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                :class="[
                  $route.name === 'dashboard'
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                ]"
              >
                Dashboard
              </RouterLink>
              <RouterLink
                to="/profile"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                :class="[
                  $route.name === 'profile'
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                ]"
              >
                Profile
              </RouterLink>
            </div>

        <!-- User Menu -->
        <div class="flex items-center space-x-4">
          <div class="hidden sm:flex items-center space-x-3">
            <div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <span class="text-xs font-medium text-gray-700">
                {{ getUserInitials }}
              </span>
            </div>
            <span class="text-sm text-gray-600 font-medium">
              {{ getUserDisplayName }}
            </span>
          </div>
          <button
            @click="handleLogout"
            class="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-all duration-200"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const getUserInitials = computed(() => {
  const user = authStore.user
  if (user?.first_name && user?.last_name) {
    return (user.first_name[0] + user.last_name[0]).toUpperCase()
  } else if (user?.first_name) {
    return user.first_name[0].toUpperCase()
  } else if (user?.email) {
    return user.email[0].toUpperCase()
  }
  return 'U'
})

const getUserDisplayName = computed(() => {
  const user = authStore.user
  if (user?.first_name && user?.last_name) {
    return `${user.first_name} ${user.last_name}`
  } else if (user?.first_name) {
    return user.first_name
  } else if (user?.email) {
    return user.email
  }
  return 'User'
})

async function handleLogout() {
  await authStore.logout()
  router.push('/auth/login')
}
</script>

