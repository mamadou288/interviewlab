import { defineStore } from 'pinia'
import { ref } from 'vue'
import { profileService } from '../services/profile'

export const useProfileStore = defineStore('profile', () => {
  const profile = ref(null)
  const cvDocument = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  async function fetchProfile() {
    isLoading.value = true
    error.value = null
    try {
      const data = await profileService.getProfile()
      profile.value = data
      if (data.cv_document) {
        cvDocument.value = data.cv_document
      }
      return data
    } catch (err) {
      error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to fetch profile'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateProfile(profileData) {
    isLoading.value = true
    error.value = null
    try {
      const data = await profileService.updateProfile(profileData)
      profile.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to update profile'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function uploadCV(file) {
    isLoading.value = true
    error.value = null
    try {
      const data = await profileService.uploadCV(file)
      cvDocument.value = data
      // Refresh profile after CV upload
      await fetchProfile()
      return data
    } catch (err) {
      error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to upload CV'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    profile,
    cvDocument,
    isLoading,
    error,
    fetchProfile,
    updateProfile,
    uploadCV,
  }
})

