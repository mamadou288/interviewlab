<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />
    <main class="section-spacing">
      <div class="container-custom">
        <!-- Header -->
        <div class="mb-8 lg:mb-12">
          <h1 class="text-4xl lg:text-5xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p class="text-gray-600 text-lg">Welcome back, {{ authStore.user?.email || 'User' }}</p>
        </div>
        
        <!-- Loading State -->
        <div v-if="analyticsStore.isLoading" class="mb-8">
          <LoadingSpinner message="Loading dashboard..." />
        </div>
        
        <!-- Content -->
        <div v-else class="space-y-8">
          <!-- Stats Grid -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
            <StatCard
              title="Overall Score"
              :value="overview?.overall_score || 0"
              color-class="text-gray-900"
            />
            <StatCard
              title="Total Sessions"
              :value="overview?.total_sessions || 0"
              color-class="text-gray-700"
            />
            <Card>
              <div class="p-6 text-center">
                <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p class="text-gray-600 font-medium">Welcome to your dashboard</p>
              </div>
            </Card>
          </div>

          <!-- Start Interview Section -->
          <Card>
            <div class="text-center py-8">
              <div class="w-16 h-16 bg-gray-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <h2 class="text-2xl font-bold text-gray-900 mb-2">Ready to Practice?</h2>
              <p class="text-gray-600 mb-6">Start a new interview session to improve your skills</p>
              <RouterLink to="/interviews/create" class="btn-primary text-lg px-8 py-3 inline-block">
                Start Interview
              </RouterLink>
            </div>
          </Card>

          <!-- Recent Interviews Section -->
          <Card v-if="recentSessions.length > 0">
            <div class="mb-6">
              <h2 class="text-2xl font-bold text-gray-900 mb-2">Recent Interviews</h2>
              <p class="text-gray-600">Your latest interview sessions</p>
            </div>
            <div class="space-y-4">
              <div
                v-for="session in recentSessions"
                :key="session.id"
                class="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                      <h3 class="text-lg font-semibold text-gray-900">
                        {{ session.role_selected?.name || 'Interview' }}
                      </h3>
                      <span
                        class="px-2 py-1 rounded text-xs font-medium capitalize"
                        :class="{
                          'bg-blue-100 text-blue-700': session.type === 'technical',
                          'bg-green-100 text-green-700': session.type === 'hr',
                          'bg-purple-100 text-purple-700': session.type === 'case',
                          'bg-gray-100 text-gray-700': session.type === 'mixed',
                        }"
                      >
                        {{ session.type }}
                      </span>
                      <span class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium capitalize">
                        {{ session.level }}
                      </span>
                    </div>
                    <div class="flex items-center gap-4 text-sm text-gray-600">
                      <span v-if="session.ended_at">
                        {{ formatDate(session.ended_at) }}
                      </span>
                      <span v-if="session.progress">
                        {{ session.progress.answered || 0 }} / {{ session.progress.total_questions || 0 }} questions
                      </span>
                    </div>
                  </div>
                  <div class="text-right">
                    <div v-if="session.overall_score !== null && session.overall_score !== undefined" class="text-2xl font-bold text-gray-900">
                      {{ session.overall_score }}
                    </div>
                    <div v-else class="text-sm text-gray-500">No score</div>
                    <div class="text-xs text-gray-500">out of 100</div>
                    <RouterLink :to="`/interviews/${session.id}`" class="btn-secondary text-sm px-3 py-1.5 mt-2 inline-block">
                      View
                    </RouterLink>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <!-- Chart Section -->
          <Card>
            <div class="mb-6">
              <h2 class="text-2xl font-bold text-gray-900 mb-2">Score Trend</h2>
              <p class="text-gray-600">Track your performance over time</p>
            </div>
            <div class="h-64 flex items-center justify-center text-gray-400 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
              <div class="text-center">
                <svg class="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p class="text-sm">Chart will be displayed here</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { RouterLink } from 'vue-router'
import { useAnalyticsStore } from '../stores/analytics'
import { useAuthStore } from '../stores/auth'
import Navbar from '../components/Navbar.vue'
import StatCard from '../components/StatCard.vue'
import Card from '../components/Card.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const analyticsStore = useAnalyticsStore()
const authStore = useAuthStore()
const recentSessions = ref([])
const isLoadingSessions = ref(false)

// Use computed to make overview reactive
const overview = computed(() => analyticsStore.overview)

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function fetchRecentSessions() {
  isLoadingSessions.value = true
  try {
    const response = await analyticsStore.fetchSessions({ limit: 5 })
    recentSessions.value = response.results || []
  } catch (err) {
    recentSessions.value = []
  } finally {
    isLoadingSessions.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    analyticsStore.fetchOverview(),
    fetchRecentSessions()
  ])
})

// Refresh data when route is activated (e.g., coming back from interview)
onActivated(async () => {
  await Promise.all([
    analyticsStore.fetchOverview(),
    fetchRecentSessions()
  ])
})
</script>

