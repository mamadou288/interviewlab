<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />
    <main class="section-spacing">
      <div class="container-custom max-w-4xl">
        <!-- Header -->
        <div class="mb-8 lg:mb-12">
          <h1 class="text-4xl lg:text-5xl font-bold text-gray-900 mb-2">Start New Interview</h1>
          <p class="text-gray-600 text-lg">Configure your interview session</p>
        </div>

        <!-- Loading State -->
        <div v-if="interviewStore.isLoading || rolesStore.isLoading || profileStore.isLoading || isParsingJobPosting" class="mb-8">
          <LoadingSpinner :message="loadingMessage" />
        </div>

        <!-- Interview Creation Form -->
        <Card v-else-if="!showPreview">
          <form @submit.prevent="handleCreateInterview" class="space-y-6">
            <!-- Upload Job Posting Section -->
            <div class="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-lg font-semibold text-gray-900">Upload Job Posting (Optional)</h3>
                <button
                  type="button"
                  @click="showJobPostingInput = !showJobPostingInput"
                  class="text-sm text-gray-600 hover:text-gray-900"
                >
                  {{ showJobPostingInput ? 'Hide' : 'Show' }}
                </button>
              </div>
              <div v-if="showJobPostingInput" class="space-y-3">
                <textarea
                  v-model="jobPostingText"
                  rows="6"
                  class="input"
                  placeholder="Paste the job posting description here..."
                ></textarea>
                <button
                  type="button"
                  @click="handleParseJobPosting"
                  :disabled="!jobPostingText.trim() || isParsingJobPosting"
                  class="btn-secondary text-sm"
                  :class="{ 'opacity-50 cursor-not-allowed': !jobPostingText.trim() || isParsingJobPosting }"
                >
                  {{ isParsingJobPosting ? 'Parsing...' : 'Parse Job Posting' }}
                </button>
                <div v-if="parsedJobPosting" class="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p class="text-sm font-medium text-green-900 mb-2">✓ Job posting parsed successfully!</p>
                  <div class="text-xs text-green-800 space-y-1">
                    <p v-if="parsedJobPosting.role_name"><strong>Role:</strong> {{ parsedJobPosting.role_name }}</p>
                    <p v-if="parsedJobPosting.level"><strong>Level:</strong> {{ parsedJobPosting.level }}</p>
                    <p v-if="parsedJobPosting.required_skills?.length"><strong>Skills:</strong> {{ parsedJobPosting.required_skills.join(', ') }}</p>
                  </div>
                </div>
                <div v-if="jobPostingError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                  {{ jobPostingError }}
                </div>
              </div>
            </div>

            <!-- Role Selection -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="block text-sm font-medium text-gray-700">Select Role</label>
                <div v-if="profileStore.profile?.data_json?.skills?.length" class="text-xs text-gray-500">
                  {{ profileStore.profile.data_json.skills.length }} skills detected
                </div>
              </div>
              
              <!-- Detected Role from CV -->
              <div v-if="detectedRole?.id && !formData.role_id" class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span class="font-medium text-blue-900">Detected from your CV: {{ detectedRole.name }}</span>
                </div>
                <button
                  @click="formData.role_id = detectedRole.id"
                  type="button"
                  class="px-3 py-1.5 bg-white border-2 border-blue-300 rounded-lg text-sm font-medium text-blue-900 hover:bg-blue-100 hover:border-blue-400 transition-all"
                >
                  Use Detected Role
                </button>
              </div>

              <!-- Suggested Roles from CV -->
              <div v-else-if="rolesStore.suggestions.length > 0 && !formData.role_id" class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <span class="font-medium text-blue-900">Suggested Roles (based on your CV)</span>
                </div>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="suggestion in rolesStore.suggestions.slice(0, 3)"
                    :key="suggestion.role.id"
                    @click="formData.role_id = suggestion.role.id"
                    type="button"
                    class="px-3 py-1.5 bg-white border-2 border-blue-300 rounded-lg text-sm font-medium text-blue-900 hover:bg-blue-100 hover:border-blue-400 transition-all"
                  >
                    {{ suggestion.role.name }}
                    <span class="text-xs text-blue-600 ml-1">({{ Math.round(suggestion.score * 100) }}% match)</span>
                  </button>
                </div>
              </div>

              <select
                v-model="formData.role_id"
                required
                class="input"
              >
                <option :value="null">Choose a role...</option>
                <optgroup v-if="rolesStore.suggestions.length > 0" label="Suggested Roles">
                  <option
                    v-for="suggestion in rolesStore.suggestions"
                    :key="suggestion.role.id"
                    :value="suggestion.role.id"
                  >
                    {{ suggestion.role.name }} ({{ Math.round(suggestion.score * 100) }}% match)
                  </option>
                </optgroup>
                <optgroup label="All Other Roles">
                  <option
                    v-for="role in allOtherRoles"
                    :key="role.id"
                    :value="role.id"
                  >
                    {{ role.name }}
                  </option>
                </optgroup>
              </select>
            </div>

            <!-- Level Selection -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="block text-sm font-medium text-gray-700">Experience Level</label>
                <div v-if="detectedLevel" class="text-xs text-blue-600 flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Detected from your CV: <span class="capitalize font-medium">{{ detectedLevel }}</span>
                </div>
              </div>
              <div class="grid grid-cols-3 gap-4">
                <label
                  v-for="level in levels"
                  :key="level.value"
                  class="flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all"
                  :class="formData.level === level.value
                    ? 'border-gray-900 bg-gray-50'
                    : 'border-gray-200 hover:border-gray-300'"
                >
                  <input
                    type="radio"
                    v-model="formData.level"
                    :value="level.value"
                    class="sr-only"
                  />
                  <div class="flex-1">
                    <div class="font-medium text-gray-900">{{ level.label }}</div>
                    <div class="text-sm text-gray-600">{{ level.description }}</div>
                  </div>
                  <svg v-if="formData.level === level.value" class="w-5 h-5 text-gray-900 ml-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </label>
              </div>
            </div>

            <!-- Interview Type Selection -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Interview Type</label>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <label
                  v-for="type in interviewTypes"
                  :key="type.value"
                  class="flex flex-col items-center p-4 border-2 rounded-lg cursor-pointer transition-all"
                  :class="formData.type === type.value
                    ? 'border-gray-900 bg-gray-50'
                    : 'border-gray-200 hover:border-gray-300'"
                >
                  <input
                    type="radio"
                    v-model="formData.type"
                    :value="type.value"
                    class="sr-only"
                  />
                  <div class="font-medium text-gray-900 mb-1">{{ type.label }}</div>
                  <div class="text-xs text-gray-600 text-center">{{ type.description }}</div>
                </label>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="interviewStore.error || rolesStore.error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {{ interviewStore.error || rolesStore.error }}
            </div>

            <!-- Submit Button -->
            <div class="flex gap-4">
              <button
                type="submit"
                :disabled="interviewStore.isLoading || !formData.role_id || !formData.level || !formData.type"
                class="btn-primary flex-1"
                :class="{ 'opacity-50 cursor-not-allowed': interviewStore.isLoading || !formData.role_id || !formData.level || !formData.type }"
              >
                {{ interviewStore.isLoading ? 'Creating...' : 'Start Interview' }}
              </button>
              <RouterLink to="/dashboard" class="btn-secondary">
                Cancel
              </RouterLink>
            </div>
          </form>
        </Card>

        <!-- Interview Preview Section -->
        <Card v-else-if="showPreview && interviewStore.currentSession">
          <div class="space-y-6">
            <div>
              <h2 class="text-2xl font-bold text-gray-900 mb-2">Interview Created Successfully!</h2>
              <p class="text-gray-600">Your interview session is ready. Here's what to expect:</p>
            </div>

            <!-- Session Info -->
            <div class="p-4 bg-gray-50 rounded-lg space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Role:</span>
                <span class="font-medium text-gray-900">{{ interviewStore.currentSession.role_selected?.name }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Level:</span>
                <span class="font-medium text-gray-900 capitalize">{{ interviewStore.currentSession.level }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Type:</span>
                <span class="font-medium text-gray-900 capitalize">{{ interviewStore.currentSession.type }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Total Questions:</span>
                <span class="font-medium text-gray-900">{{ interviewStore.questions.length }}</span>
              </div>
            </div>

            <!-- Questions Preview -->
            <div v-if="interviewStore.questions.length > 0">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Questions Preview</h3>
              <div class="space-y-3 max-h-96 overflow-y-auto">
                <div
                  v-for="(question, index) in interviewStore.questions.slice(0, 5)"
                  :key="question.id"
                  class="p-3 bg-white border border-gray-200 rounded-lg"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-gray-500">Question {{ index + 1 }}</span>
                    <span
                      class="px-2 py-0.5 rounded text-xs font-medium"
                      :class="{
                        'bg-blue-100 text-blue-700': question.category === 'technical',
                        'bg-green-100 text-green-700': question.category === 'hr',
                        'bg-purple-100 text-purple-700': question.category === 'case',
                        'bg-gray-100 text-gray-700': question.category === 'behavioral',
                      }"
                    >
                      {{ question.category }}
                    </span>
                  </div>
                  <p class="text-gray-800">{{ question.question_text }}</p>
                </div>
              </div>
              <p v-if="interviewStore.questions.length > 5" class="text-sm text-gray-500 mt-3">
                And {{ interviewStore.questions.length - 5 }} more questions...
              </p>
            </div>

            <!-- Action Buttons -->
            <div class="flex gap-4 pt-4">
              <button
                @click="startInterview"
                class="btn-primary flex-1"
              >
                Start Interview
              </button>
              <button
                @click="showPreview = false; formData.role_id = null; formData.level = null; formData.type = null; parsedJobPosting = null; jobPostingText = ''; jobPostingError = null;"
                class="btn-secondary"
              >
                Create Another
              </button>
            </div>
          </div>
        </Card>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useInterviewStore } from '../stores/interviews'
import { useRolesStore } from '../stores/roles'
import { useProfileStore } from '../stores/profile'
import { jobPostingService } from '../services/jobPosting'
import { determineLevel } from '../utils/levelDetector'
import Navbar from '../components/Navbar.vue'
import Card from '../components/Card.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const interviewStore = useInterviewStore()
const rolesStore = useRolesStore()
const profileStore = useProfileStore()

const showPreview = ref(false)
const showJobPostingInput = ref(false)
const jobPostingText = ref('')
const isParsingJobPosting = ref(false)
const parsedJobPosting = ref(null)
const jobPostingError = ref(null)

const formData = ref({
  role_id: null,
  level: null,
  type: null,
})

const loadingMessage = computed(() => {
  if (isParsingJobPosting.value) return 'Parsing job posting...'
  if (interviewStore.isLoading) return 'Creating interview session...'
  if (rolesStore.isLoading) return 'Loading roles...'
  if (profileStore.isLoading) return 'Loading profile...'
  return 'Loading...'
})

// Detect level from profile data
const detectedLevel = computed(() => {
  if (profileStore.profile?.data_json) {
    return determineLevel(profileStore.profile.data_json)
  }
  return null
})

// Get detected role from profile data
const detectedRole = computed(() => {
  if (profileStore.profile?.data_json?.detected_role_id && rolesStore.roles.length > 0) {
    return rolesStore.roles.find(r => r.id === profileStore.profile.data_json.detected_role_id)
  }
  return null
})

// Get roles that are not in suggestions
const allOtherRoles = computed(() => {
  if (!rolesStore.suggestions.length) {
    return rolesStore.roles
  }
  const suggestedRoleIds = new Set(rolesStore.suggestions.map(s => s.role.id))
  return rolesStore.roles.filter(role => !suggestedRoleIds.has(role.id))
})

const levels = [
  { value: 'junior', label: 'Junior', description: 'Entry level' },
  { value: 'mid', label: 'Mid-level', description: '2-5 years' },
  { value: 'senior', label: 'Senior', description: '5+ years' },
]

const interviewTypes = [
  { value: 'hr', label: 'HR', description: 'General questions' },
  { value: 'technical', label: 'Technical', description: 'Technical skills' },
  { value: 'case', label: 'Case Study', description: 'Problem solving' },
  { value: 'mixed', label: 'Mixed', description: 'All types' },
]

async function handleCreateInterview() {
  try {
    const session = await interviewStore.createSession(formData.value)
    await interviewStore.fetchQuestions(session.id)
    showPreview.value = true
  } catch (err) {
    // Error handled by store
  }
}

async function startInterview() {
  router.push(`/interviews/${interviewStore.currentSession.id}`)
}

async function handleParseJobPosting() {
  if (!jobPostingText.value.trim()) return

  isParsingJobPosting.value = true
  jobPostingError.value = null
  parsedJobPosting.value = null

  try {
    const response = await jobPostingService.parseJobPosting(jobPostingText.value)
    parsedJobPosting.value = response

    // Auto-fill form based on parsed data
    if (response.level && levels.some(l => l.value === response.level)) {
      formData.value.level = response.level
    }
    if (response.detected_role_id) {
      formData.value.role_id = response.detected_role_id
    } else if (response.role_name) {
      const matchedRole = rolesStore.roles.find(r => r.name.toLowerCase() === response.role_name.toLowerCase())
      if (matchedRole) {
        formData.value.role_id = matchedRole.id
      }
    }
  } catch (err) {
    jobPostingError.value = err.response?.data?.error || 'Failed to parse job posting.'
  } finally {
    isParsingJobPosting.value = false
  }
}

onMounted(async () => {
  await rolesStore.fetchRoles()
  
  try {
    await profileStore.fetchProfile()
    
    // Auto-select level
    if (profileStore.profile?.data_json) {
      const level = determineLevel(profileStore.profile.data_json)
      if (level && !formData.value.level) {
        formData.value.level = level
      }
    }
    
    // Auto-select role
    const detectedRoleId = profileStore.profile?.data_json?.detected_role_id
    if (detectedRoleId && !formData.value.role_id) {
      formData.value.role_id = detectedRoleId
    } else {
      const cvId = profileStore.profile?.cv_document?.id
      if (cvId) {
        try {
          await rolesStore.fetchSuggestions(cvId)
          if (rolesStore.suggestions.length > 0 && !formData.value.role_id) {
            formData.value.role_id = rolesStore.suggestions[0].role.id
          }
        } catch (err) {
          // Silently fail
        }
      }
    }
  } catch (err) {
    // Profile might not exist yet, that's okay
  }
})

// Watch for profile changes to auto-select level and role
watch(() => profileStore.profile, (newProfile) => {
  if (newProfile?.data_json) {
    const level = determineLevel(newProfile.data_json)
    if (level && !formData.value.level) {
      formData.value.level = level
    }

    const detectedRoleId = newProfile.data_json.detected_role_id
    if (detectedRoleId && !formData.value.role_id) {
      formData.value.role_id = detectedRoleId
    }
  }
}, { immediate: true, deep: true })

// Watch for roles to be loaded, then try to auto-select detected role
watch(() => rolesStore.roles, (newRoles) => {
  if (newRoles.length > 0 && profileStore.profile?.data_json?.detected_role_id && !formData.value.role_id) {
    const roleId = profileStore.profile.data_json.detected_role_id
    const role = newRoles.find(r => r.id === roleId)
    if (role) {
      formData.value.role_id = roleId
    }
  }
}, { immediate: true, deep: true })
</script>
