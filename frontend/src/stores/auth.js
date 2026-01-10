import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('accessToken'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))
  const isLoading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => {
    // Check if we have a token, even if user is not loaded yet
    return !!accessToken.value
  })

  async function login(email, password) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authService.login(email, password)
      accessToken.value = response.access
      refreshToken.value = response.refresh
      user.value = response.user
      
      localStorage.setItem('accessToken', response.access)
      localStorage.setItem('refreshToken', response.refresh)
      
      return response
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function register(email, password, password2, firstName, lastName) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authService.register(email, password, password2, firstName, lastName)
      
      // Validate response structure
      if (!response || !response.access || !response.refresh) {
        throw new Error('Invalid response from server: missing access or refresh token')
      }
      
      accessToken.value = response.access
      refreshToken.value = response.refresh
      user.value = response.user
      
      localStorage.setItem('accessToken', response.access)
      localStorage.setItem('refreshToken', response.refresh)
      
      return response
    } catch (err) {
      // Handle network errors
      if (err.isNetworkError || !err.response) {
        error.value = err.message || 'Network Error: Unable to connect to the server. Please make sure the backend is running on http://localhost:8000'
        throw err
      }
      
      if (err.response?.data) {
        const errorData = err.response.data
        // Handle different error formats
        if (errorData.password) {
          error.value = Array.isArray(errorData.password) 
            ? errorData.password.join(', ') 
            : errorData.password
        } else if (errorData.email) {
          error.value = Array.isArray(errorData.email) 
            ? errorData.email.join(', ') 
            : errorData.email
        } else if (errorData.detail) {
          error.value = errorData.detail
        } else if (errorData.non_field_errors) {
          error.value = Array.isArray(errorData.non_field_errors) 
            ? errorData.non_field_errors.join(', ') 
            : errorData.non_field_errors
        } else {
          // Show first error found
          const firstError = Object.values(errorData)[0]
          error.value = Array.isArray(firstError) ? firstError[0] : firstError
        }
      } else if (err.message) {
        error.value = err.message
      } else {
        error.value = 'Registration failed. Please try again.'
      }
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      await authService.logout()
    } catch (err) {
      // Silently fail - clear local state anyway
    } finally {
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }
    
    try {
      const response = await authService.refreshToken(refreshToken.value)
      accessToken.value = response.access
      localStorage.setItem('accessToken', response.access)
      return response.access
    } catch (err) {
      // Refresh failed, logout user
      await logout()
      throw err
    }
  }

  function setUser(userData) {
    user.value = userData
  }

  return {
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    refreshAccessToken,
    setUser,
  }
})

