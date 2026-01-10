import apiClient from './api'

export const analyticsService = {
  async getOverview() {
    const response = await apiClient.get('/analytics/overview')
    return response.data
  },

  async getSessions(params) {
    const response = await apiClient.get('/analytics/sessions', { params })
    return response.data
  },
}

