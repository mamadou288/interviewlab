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
import { computed, onMounted } from 'vue'
import { useAnalyticsStore } from '../stores/analytics'
import { useAuthStore } from '../stores/auth'
import Navbar from '../components/Navbar.vue'
import StatCard from '../components/StatCard.vue'
import Card from '../components/Card.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const analyticsStore = useAnalyticsStore()
const authStore = useAuthStore()

// Use computed to make overview reactive
const overview = computed(() => analyticsStore.overview)

onMounted(async () => {
  await analyticsStore.fetchOverview()
})
</script>

