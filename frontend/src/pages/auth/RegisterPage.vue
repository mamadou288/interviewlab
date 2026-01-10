<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo -->
      <div class="text-center">
        <div class="flex justify-center mb-6">
          <div class="w-16 h-16 bg-gray-900 rounded-2xl flex items-center justify-center">
            <span class="text-white font-bold text-2xl">IL</span>
          </div>
        </div>
        <h2 class="text-3xl lg:text-4xl font-bold text-gray-900 mb-2">
          Create your account
        </h2>
        <p class="text-gray-600">Get started with InterviewLab</p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="space-y-4">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="input mt-1 bg-white"
              placeholder="your@email.com"
            />
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="input mt-1 bg-white"
              placeholder="Password"
            />
          </div>
          <div>
            <label for="password2" class="block text-sm font-medium text-gray-700">Confirm Password</label>
            <input
              id="password2"
              v-model="password2"
              type="password"
              required
              class="input mt-1 bg-white"
              placeholder="Confirm password"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="firstName" class="block text-sm font-medium text-gray-700">First Name</label>
              <input
                id="firstName"
                v-model="firstName"
                type="text"
                class="input mt-1 bg-white"
                placeholder="John"
              />
            </div>
            <div>
              <label for="lastName" class="block text-sm font-medium text-gray-700">Last Name</label>
              <input
                id="lastName"
                v-model="lastName"
                type="text"
                class="input mt-1 bg-white"
                placeholder="Doe"
              />
            </div>
          </div>
        </div>

        <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          <div class="flex items-start">
            <svg class="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <div class="flex-1">
              <strong class="font-medium">Registration Failed</strong>
              <p class="mt-1 whitespace-pre-line">{{ error }}</p>
              <div v-if="error.includes('Network Error') || error.includes('Unable to connect')" class="mt-3 p-2 bg-red-100 rounded text-xs">
                <p class="font-semibold mb-1">💡 Diagnostic:</p>
                <p class="mb-2">The backend is responding (200), but the response isn't reaching the frontend. This is likely a CORS issue.</p>
                <p class="mb-1"><strong>Steps to fix:</strong></p>
                <ol class="list-decimal list-inside space-y-1 ml-2">
                  <li>Open browser console (F12) → Network tab</li>
                  <li>Try registering again</li>
                  <li>Check if you see CORS errors</li>
                  <li>Verify backend CORS settings include: <code class="bg-white px-1 rounded">http://localhost:5173</code></li>
                </ol>
                <p class="mt-2 text-xs text-gray-600">Check console for detailed error logs (📤 Request, ✅ Response, ❌ Error)</p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading || !passwordsMatch || !email || !password || !password2"
            :class="[
              'w-full rounded-lg font-medium transition-all duration-200',
              (isLoading || !passwordsMatch || !email || !password || !password2)
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed px-6 py-3'
                : 'btn-primary'
            ]"
          >
            {{ isLoading ? 'Creating account...' : 'Create account' }}
          </button>
          <p v-if="password && password2 && !passwordsMatch" class="mt-2 text-sm text-red-600 text-center">
            Passwords do not match
          </p>
          <p v-if="(!email || !password || !password2) && (email || password || password2)" class="mt-2 text-sm text-gray-500 text-center">
            Please fill in all required fields
          </p>
        </div>

        <div class="text-center pt-4">
          <p class="text-sm text-gray-600">
            Already have an account?
            <RouterLink to="/auth/login" class="font-medium text-gray-900 hover:text-gray-700 transition-colors">
              Login
            </RouterLink>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const password2 = ref('')
const firstName = ref('')
const lastName = ref('')
const isLoading = ref(false)
const error = ref(null)

const passwordsMatch = computed(() => {
  if (!password.value || !password2.value) return false
  return password.value === password2.value
})


async function handleRegister() {
  // Validate required fields
  if (!email.value || !password.value || !password2.value) {
    error.value = 'Please fill in all required fields'
    return
  }
  
  // Validate password match
  if (!passwordsMatch.value) {
    error.value = 'Passwords do not match'
    return
  }
  
  // Prevent double submission
  if (isLoading.value) {
    return
  }
  
  isLoading.value = true
  error.value = null
  
  try {
    await authStore.register(
      email.value,
      password.value,
      password2.value,
      firstName.value || undefined,
      lastName.value || undefined
    )
    
    router.push('/dashboard')
  } catch (err) {
    // Use error from store (already formatted)
    error.value = authStore.error || err.message || 'Registration failed. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

