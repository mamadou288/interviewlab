import { defineStore } from 'pinia'
import { ref } from 'vue'
import { rolesService } from '../services/roles'

export const useRolesStore = defineStore('roles', () => {
  const roles = ref([])
  const suggestions = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  async function fetchRoles(category = null) {
    isLoading.value = true
    error.value = null
    try {
      const data = await rolesService.getRoles(category)
      roles.value = data.results || data || []
      return roles.value
    } catch (err) {
      error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to fetch roles'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSuggestions(cvId) {
    isLoading.value = true
    error.value = null
    try {
      const data = await rolesService.getRoleSuggestions(cvId)
      suggestions.value = data.suggestions || data.results || data || []
      return suggestions.value
    } catch (err) {
      error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to fetch role suggestions'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    roles,
    suggestions,
    isLoading,
    error,
    fetchRoles,
    fetchSuggestions,
  }
})

