<template>
  <div class="min-h-screen bg-gray-50">
    <LandingNavbar />
    
    <!-- Hero Section -->
    <section class="section-spacing">
      <div class="container-custom">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Manage Your Professional Profile
            <span class="block text-gray-600 mt-2">with AI-Powered CV Analysis</span>
          </h1>
          <p class="text-xl text-gray-600 mb-8 leading-relaxed">
            InterviewLab helps you manage your professional profile and CV. 
            Upload your CV to extract skills, experience, and education automatically.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <RouterLink to="/auth/register" class="btn-primary text-base px-8 py-4">
              Get Started
            </RouterLink>
            <RouterLink to="/auth/login" class="btn-secondary text-base px-8 py-4">
              Sign In
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="section-spacing bg-white">
      <div class="container-custom">
        <div class="max-w-6xl mx-auto">
          <h2 class="text-3xl lg:text-4xl font-bold text-gray-900 text-center mb-12">
            Why InterviewLab?
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Feature 1 -->
            <div class="text-center">
              <div class="w-16 h-16 bg-gray-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">AI-Powered CV Analysis</h3>
              <p class="text-gray-600">
                Upload your CV and let AI automatically extract your skills, experience, and education details.
              </p>
            </div>

            <!-- Feature 2 -->
            <div class="text-center">
              <div class="w-16 h-16 bg-gray-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">Track Your Profile</h3>
              <p class="text-gray-600">
                View your extracted profile data, manage your CV, and keep your professional information up to date.
              </p>
            </div>

            <!-- Feature 3 -->
            <div class="text-center">
              <div class="w-16 h-16 bg-gray-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">Easy Management</h3>
              <p class="text-gray-600">
                Easily update your CV and profile information. Replace your CV anytime with a single click.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="section-spacing">
      <div class="container-custom">
        <div class="max-w-3xl mx-auto text-center">
          <div class="card bg-gray-900 text-white">
            <h2 class="text-3xl lg:text-4xl font-bold mb-4">Ready to Get Started?</h2>
            <p class="text-xl text-gray-300 mb-8">
              Join InterviewLab today and start managing your professional profile with AI-powered CV analysis.
            </p>
            <RouterLink to="/auth/register" class="btn-secondary bg-white text-gray-900 hover:bg-gray-100 inline-block">
              Start Practicing Now
            </RouterLink>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import LandingNavbar from '../components/LandingNavbar.vue'
</script>

