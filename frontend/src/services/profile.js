import apiClient from './api'

export const profileService = {
  async getProfile() {
    const response = await apiClient.get('/profile/me')
    return response.data
  },

  async updateProfile(data) {
    const response = await apiClient.patch('/profile/me', data)
    return response.data
  },

  async uploadCV(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post('/cv/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getCVDocument(id) {
    const response = await apiClient.get(`/cv/${id}`)
    return response.data
  },
}

