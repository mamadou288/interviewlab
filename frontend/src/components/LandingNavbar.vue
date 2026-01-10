<template>
  <nav class="bg-white border-b border-gray-200 sticky top-0 z-50 backdrop-blur-sm bg-white/95">
    <div class="container-custom">
      <div class="flex justify-between items-center h-16 lg:h-20">
        <!-- Logo/Brand -->
        <RouterLink to="/" class="flex items-center space-x-2 group">
          <div class="w-8 h-8 bg-gray-900 rounded-lg flex items-center justify-center group-hover:bg-gray-800 transition-colors">
            <span class="text-white font-bold text-sm">IL</span>
          </div>
          <span class="text-xl font-bold text-gray-900 hidden sm:block">InterviewLab</span>
        </RouterLink>

        <!-- Navigation Links -->
        <div class="flex items-center space-x-4">
          <RouterLink
            to="/auth/login"
            class="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
          >
            Sign In
          </RouterLink>
          <RouterLink
            to="/auth/register"
            class="btn-primary text-sm"
          >
            Get Started
          </RouterLink>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

