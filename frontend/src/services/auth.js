import apiClient from './api'

export const authService = {
  async login(email, password) {
    const response = await apiClient.post('/auth/login', {
      email,
      password,
    })
    return response.data
  },

  async register(email, password, password2, firstName, lastName) {
    const response = await apiClient.post('/auth/register', {
      email,
      password,
      password2,
      first_name: firstName,
      last_name: lastName,
    })
    return response.data
  },

  async logout() {
    await apiClient.post('/auth/logout')
  },

  async refreshToken(refresh) {
    const response = await apiClient.post('/auth/refresh', {
      refresh,
    })
    return response.data
  },
}

