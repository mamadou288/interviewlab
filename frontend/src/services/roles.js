import apiClient from './api'

export const rolesService = {
  async getRoles(category = null) {
    const params = category ? { category } : {}
    const response = await apiClient.get('/roles', { params })
    return response.data
  },

  async getRoleSuggestions(cvId) {
    const response = await apiClient.get(`/cv/${cvId}/role-suggestions`)
    return response.data
  },
}

