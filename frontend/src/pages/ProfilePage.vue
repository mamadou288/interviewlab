<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />
    <main class="section-spacing">
      <div class="container-custom">
        <!-- Header -->
        <div class="mb-8 lg:mb-12">
          <h1 class="text-4xl lg:text-5xl font-bold text-gray-900 mb-2">Profile</h1>
          <p class="text-gray-600 text-lg">Manage your profile and CV</p>
        </div>
      
        <!-- Loading State -->
        <div v-if="profileStore.isLoading && !profileStore.profile" class="mb-8">
        <LoadingSpinner message="Loading profile..." />
      </div>
      
        <!-- Content -->
        <div v-else class="space-y-8">
        <!-- User Information Card -->
          <Card>
            <h2 class="text-2xl font-bold text-gray-900 mb-6">User Information</h2>
            <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <p class="text-gray-900">{{ profileStore.profile?.user_email || authStore.user?.email || 'N/A' }}</p>
              </div>
              <div v-if="profileStore.profile?.user_first_name || profileStore.profile?.user_last_name || authStore.user?.first_name || authStore.user?.last_name">
                <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <p class="text-gray-900">
                  {{ getUserFullName }}
              </p>
            </div>
            </div>
          </Card>

          <!-- CV Upload Section -->
          <Card>
            <h2 class="text-2xl font-bold text-gray-900 mb-6">CV Document</h2>
            
            <!-- CV Upload Form -->
            <div v-if="!profileStore.cvDocument" class="space-y-4">
              <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="text-gray-600 mb-2">Upload your CV to get started</p>
                <p class="text-sm text-gray-500 mb-4">Supports PDF and DOCX files (max 10MB)</p>
                <input
                  ref="fileInput"
                  type="file"
                  accept=".pdf,.docx"
                  @change="handleFileSelect"
                  class="hidden"
                  id="cv-upload"
                />
                <label
                  for="cv-upload"
                  class="btn-primary inline-block cursor-pointer"
                >
                  Choose File
                </label>
                <p v-if="selectedFile" class="mt-2 text-sm text-gray-600">
                  Selected: {{ selectedFile.name }}
                </p>
              </div>
              <div v-if="selectedFile" class="flex gap-4">
                <button
                  @click="handleUpload"
                  :disabled="isUploading"
                  class="btn-primary"
                >
                  {{ isUploading ? 'Uploading...' : 'Upload CV' }}
                </button>
                <button
                  @click="selectedFile = null"
                  :disabled="isUploading"
                  class="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>

            <!-- CV Status -->
            <div v-else class="space-y-4">
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">CV Document</p>
                    <p class="text-sm text-gray-600">
                      Status: 
                      <span :class="{
                        'text-green-600': profileStore.cvDocument?.status === 'completed',
                        'text-yellow-600': profileStore.cvDocument?.status === 'processing',
                        'text-red-600': profileStore.cvDocument?.status === 'failed'
                      }">
                        {{ getStatusLabel(profileStore.cvDocument?.status) }}
                      </span>
                    </p>
                    <p v-if="profileStore.cvDocument?.created_at" class="text-xs text-gray-500 mt-1">
                      Uploaded: {{ formatDate(profileStore.cvDocument.created_at) }}
                    </p>
                  </div>
                </div>
                <div>
                  <span
                    class="px-3 py-1 rounded-full text-xs font-medium"
                    :class="{
                      'bg-green-100 text-green-700': profileStore.cvDocument?.status === 'completed',
                      'bg-yellow-100 text-yellow-700': profileStore.cvDocument?.status === 'processing',
                      'bg-red-100 text-red-700': profileStore.cvDocument?.status === 'failed'
                    }"
                  >
                    {{ getStatusLabel(profileStore.cvDocument?.status) }}
                  </span>
            </div>
          </div>
              
              <!-- Replace CV Section -->
              <div v-if="!selectedFile" class="space-y-2">
                <input
                  ref="replaceFileInput"
                  type="file"
                  accept=".pdf,.docx"
                  @change="handleFileSelect"
                  class="hidden"
                  id="cv-replace"
                />
                <button
                  @click="triggerReplaceCV"
                  :disabled="isUploading"
                  class="btn-secondary w-full sm:w-auto"
                >
                  Replace CV
                </button>
        </div>

              <!-- File Selected for Replace -->
              <div v-if="selectedFile" class="space-y-4">
                <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p class="text-sm font-medium text-blue-900 mb-1">New file selected:</p>
                  <p class="text-sm text-blue-700">{{ selectedFile.name }}</p>
                </div>
                <div class="flex gap-4">
                  <button
                    @click="handleUpload"
                    :disabled="isUploading"
              class="btn-primary"
            >
                    {{ isUploading ? 'Uploading...' : 'Upload New CV' }}
                  </button>
                  <button
                    @click="cancelReplace"
                    :disabled="isUploading"
                class="btn-secondary"
              >
                    Cancel
                  </button>
                </div>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="profileStore.error" class="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {{ profileStore.error }}
          </div>
          </Card>

          <!-- Profile Data Section -->
          <Card v-if="profileStore.profile?.data_json">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Extracted Profile Data</h2>
            
            <!-- Skills -->
            <div v-if="profileStore.profile?.data_json?.skills?.length" class="mb-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Skills</h3>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="(skill, index) in profileStore.profile.data_json.skills"
                  :key="index"
                  class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  {{ skill }}
                </span>
              </div>
            </div>

            <!-- Experience -->
            <div v-if="profileStore.profile?.data_json?.experience?.length" class="mb-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Experience</h3>
              <div class="space-y-4">
                <div
                  v-for="(exp, index) in profileStore.profile.data_json.experience"
                  :key="index"
                  class="border-l-2 border-gray-200 pl-4"
                >
                  <h4 class="font-medium text-gray-900">{{ exp.title }}</h4>
                  <p v-if="exp.company" class="text-gray-600">{{ exp.company }}</p>
                  <p v-if="exp.dates || exp.period" class="text-sm text-gray-500">{{ exp.dates || exp.period }}</p>
                  <div v-if="exp.description" class="text-gray-600 mt-2">
                    <ul v-if="Array.isArray(exp.description)" class="list-disc list-inside space-y-1">
                      <li v-for="(desc, descIndex) in exp.description" :key="descIndex">{{ desc }}</li>
                    </ul>
                    <p v-else class="whitespace-pre-line">{{ exp.description }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Education -->
            <div v-if="profileStore.profile.data_json.education?.length" class="mb-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Education</h3>
              <div class="space-y-4">
                <div
                  v-for="(edu, index) in profileStore.profile.data_json.education"
                  :key="index"
                  class="border-l-2 border-gray-200 pl-4"
                >
                  <h4 class="font-medium text-gray-900">{{ edu.degree }}</h4>
                  <p class="text-gray-600">{{ edu.institution }}</p>
                  <p v-if="edu.dates" class="text-sm text-gray-500">{{ edu.dates }}</p>
          </div>
          </div>
        </div>

            <!-- Projects -->
            <div v-if="profileStore.profile?.data_json?.projects?.length">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Projects</h3>
              <div class="space-y-4">
                <div
                  v-for="(project, index) in profileStore.profile.data_json.projects"
                  :key="index"
                  class="border-l-2 border-gray-200 pl-4"
                >
                  <h4 class="font-medium text-gray-900">{{ project.name || project.title || `Project ${index + 1}` }}</h4>
                  <p v-if="project.description" class="text-gray-600 mt-1 whitespace-pre-line">{{ project.description }}</p>
                  <div v-if="project.technologies && Array.isArray(project.technologies) && project.technologies.length > 0" class="mt-2 flex flex-wrap gap-2">
                    <span
                      v-for="(tech, techIndex) in project.technologies"
                      :key="techIndex"
                      class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                    >
                      {{ tech }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <!-- Empty State -->
          <Card v-else-if="profileStore.cvDocument?.status === 'completed'">
            <div class="text-center py-8">
              <p class="text-gray-600">No profile data extracted yet. Please wait for processing to complete.</p>
            </div>
          </Card>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProfileStore } from '../stores/profile'
import { useAuthStore } from '../stores/auth'
import Navbar from '../components/Navbar.vue'
import Card from '../components/Card.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const profileStore = useProfileStore()
const authStore = useAuthStore()
const selectedFile = ref(null)
const isUploading = ref(false)
const fileInput = ref(null)
const replaceFileInput = ref(null)

// Get user full name from profile or auth store
const getUserFullName = computed(() => {
  const profile = profileStore.profile
  const user = authStore.user
  
  if (profile?.user_first_name || profile?.user_last_name) {
    return [profile.user_first_name, profile.user_last_name].filter(Boolean).join(' ') || 'N/A'
  } else if (user?.first_name || user?.last_name) {
    return [user.first_name, user.last_name].filter(Boolean).join(' ') || 'N/A'
  }
  return 'N/A'
})

// All extraction logic should be handled by the backend
// Frontend only displays what backend sends

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    // Validate file type
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    const validExtensions = ['.pdf', '.docx']
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
    
    if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
      profileStore.error = 'Please upload a PDF or DOCX file'
      return
    }
    
    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      profileStore.error = 'File size must be less than 10MB'
      return
    }
    
    selectedFile.value = file
    profileStore.error = null
  }
}

function triggerReplaceCV() {
  const input = document.getElementById('cv-replace')
  if (input) {
    input.click()
  }
}

function cancelReplace() {
  selectedFile.value = null
  if (replaceFileInput.value) {
    replaceFileInput.value.value = ''
  }
}

async function handleUpload() {
  if (!selectedFile.value) return
  
  isUploading.value = true
  try {
    await profileStore.uploadCV(selectedFile.value)
    selectedFile.value = null
    // Reset file inputs
    if (fileInput.value) fileInput.value.value = ''
    if (replaceFileInput.value) replaceFileInput.value.value = ''
  } catch (err) {
    // Error handled by store
  } finally {
    isUploading.value = false
  }
}

function getStatusLabel(status) {
  const statusMap = {
    'uploaded': 'Uploaded',
    'processing': 'Processing',
    'completed': 'Completed',
    'failed': 'Failed'
  }
  return statusMap[status] || status || 'Unknown'
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(async () => {
  await profileStore.fetchProfile()
})
</script>

