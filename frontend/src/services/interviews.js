import apiClient from './api'

export const interviewService = {
  async createSession(data) {
    const response = await apiClient.post('/interviews', data)
    return response.data
  },

  async getSession(id) {
    const response = await apiClient.get(`/interviews/${id}`)
    return response.data
  },

  async getQuestions(id) {
    const response = await apiClient.get(`/interviews/${id}/questions`)
    return response.data
  },

  async submitAnswer(id, answerData) {
    const response = await apiClient.post(`/interviews/${id}/answers`, answerData)
    return response.data
  },

  async finishSession(id) {
    const response = await apiClient.patch(`/interviews/${id}/finish`)
    return response.data
  },

  async getReport(id) {
    const response = await apiClient.get(`/interviews/${id}/report`)
    return response.data
  },
}

