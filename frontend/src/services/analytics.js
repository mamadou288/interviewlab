import apiClient from './api'

export const analyticsService = {
  async getOverview() {
    const response = await apiClient.get('/analytics/overview')
    return response.data
  },
}

