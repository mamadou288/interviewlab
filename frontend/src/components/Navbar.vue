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
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useProfileStore } from '../stores/profile'

const router = useRouter()
const authStore = useAuthStore()
const profileStore = useProfileStore()

// Try to get user data from profile if not in auth store
onMounted(async () => {
  if (!authStore.user && authStore.isAuthenticated) {
    try {
      await profileStore.fetchProfile()
      if (profileStore.profile) {
        authStore.setUser({
          email: profileStore.profile.user_email,
          first_name: profileStore.profile.user_first_name,
          last_name: profileStore.profile.user_last_name,
        })
      }
    } catch (err) {
      // Silently fail - user might not have profile yet
    }
  }
})

const getUserInitials = computed(() => {
  // Try auth store user first
  let firstName = authStore.user?.first_name?.trim() || ''
  let lastName = authStore.user?.last_name?.trim() || ''
  
  // Fallback to profile store if auth store doesn't have name
  if (!firstName && profileStore.profile?.user_first_name) {
    firstName = profileStore.profile.user_first_name.trim()
  }
  if (!lastName && profileStore.profile?.user_last_name) {
    lastName = profileStore.profile.user_last_name.trim()
  }
  
  // If both first_name and last_name exist and are not empty
  if (firstName && lastName) {
    // Get first letter of first name and first letter of last name
    const firstInitial = firstName[0].toUpperCase()
    const lastInitial = lastName[0].toUpperCase()
    return firstInitial + lastInitial
  }
  
  // If only first_name exists and is not empty
  if (firstName) {
    // Use first two letters if available, otherwise just first letter
    return firstName.length >= 2 
      ? firstName.substring(0, 2).toUpperCase()
      : firstName[0].toUpperCase()
  }
  
  // Fallback to email first letter
  const email = authStore.user?.email?.trim() || profileStore.profile?.user_email?.trim() || ''
  if (email) {
    return email[0].toUpperCase()
  }
  
  return 'U'
})

const getUserDisplayName = computed(() => {
  // Try auth store user first
  let firstName = authStore.user?.first_name?.trim() || ''
  
  // Fallback to profile store if auth store doesn't have name
  if (!firstName && profileStore.profile?.user_first_name) {
    firstName = profileStore.profile.user_first_name.trim()
  }
  
  // Show only first name if it exists and is not empty
  if (firstName) {
    return firstName
  }
  
  // Fallback to email username part
  const email = authStore.user?.email?.trim() || profileStore.profile?.user_email?.trim() || ''
  if (email) {
    const emailName = email.split('@')[0]
    return emailName.charAt(0).toUpperCase() + emailName.slice(1)
  }
  
  return 'User'
})

async function handleLogout() {
  await authStore.logout()
  router.push('/auth/login')
}
</script>

