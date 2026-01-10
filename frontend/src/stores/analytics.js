import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analyticsService } from '../services/analytics'

export const useAnalyticsStore = defineStore('analytics', () => {
  const overview = ref(null)
  const skills = ref([])
  const sessions = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  async function fetchOverview() {
    isLoading.value = true
    error.value = null
    try {
      const data = await analyticsService.getOverview()
      overview.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch overview'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSessions(filters) {
    isLoading.value = true
    error.value = null
    try {
      const data = await analyticsService.getSessions(filters)
      sessions.value = data.results
      return data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch sessions'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    overview,
    sessions,
    isLoading,
    error,
    fetchOverview,
    fetchSessions,
  }
})

