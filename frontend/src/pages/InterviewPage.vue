<template>
  <div class="min-h-screen bg-gray-50">
    <main class="section-spacing">
      <div class="container-custom max-w-4xl">
        <!-- Loading State -->
        <div v-if="interviewStore.isLoading && !interviewStore.currentSession" class="mb-8">
          <LoadingSpinner message="Loading interview..." />
        </div>

        <!-- Interview Content -->
        <div v-else-if="interviewStore.currentSession" class="space-y-6">
          <!-- Header -->
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-3xl lg:text-4xl font-bold text-gray-900 mb-2">
                {{ interviewStore.currentSession.role_selected?.name || 'Interview' }}
              </h1>
              <p class="text-gray-600">
                {{ interviewStore.currentSession.type }} • {{ interviewStore.currentSession.level }}
              </p>
            </div>
            <div class="text-right">
              <div class="text-sm text-gray-600">Progress</div>
              <div class="text-lg font-semibold text-gray-900">
                {{ progress.current_question || 0 }} / {{ progress.total_questions || 0 }}
              </div>
            </div>
          </div>

          <!-- Progress Bar -->
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-gray-900 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${progressPercentage}%` }"
            ></div>
          </div>

          <!-- Question Section -->
          <Card v-if="currentQuestion">
            <div class="space-y-6">
              <!-- Question Header -->
              <div>
                <div class="flex items-center justify-between mb-4">
                  <span class="text-sm font-medium text-gray-500">
                    Question {{ currentQuestionIndex + 1 }} of {{ interviewStore.questions.length }}
                  </span>
                  <span
                    class="px-2 py-1 rounded text-xs font-medium"
                    :class="{
                      'bg-blue-100 text-blue-700': currentQuestion.category === 'technical',
                      'bg-green-100 text-green-700': currentQuestion.category === 'hr',
                      'bg-purple-100 text-purple-700': currentQuestion.category === 'case',
                      'bg-gray-100 text-gray-700': currentQuestion.category === 'behavioral',
                    }"
                  >
                    {{ currentQuestion.category }}
                  </span>
                </div>
                <h2 class="text-xl lg:text-2xl font-bold text-gray-900 mb-4">
                  {{ currentQuestion.question_text }}
                </h2>
              </div>

              <!-- Answer Input -->
              <div v-if="!currentQuestion.answer">
                <label class="block text-sm font-medium text-gray-700 mb-2">Your Answer</label>
                <textarea
                  v-model="answerText"
                  rows="8"
                  class="input"
                  placeholder="Type your answer here..."
                ></textarea>
                <div class="mt-4 flex gap-4">
                  <button
                    @click="handleSubmitAnswer"
                    :disabled="!answerText.trim() || interviewStore.isLoading"
                    class="btn-primary"
                    :class="{ 'opacity-50 cursor-not-allowed': !answerText.trim() || interviewStore.isLoading }"
                  >
                    {{ interviewStore.isLoading ? 'Submitting...' : 'Submit Answer' }}
                  </button>
                  <button
                    v-if="currentQuestionIndex < interviewStore.questions.length - 1"
                    @click="skipQuestion"
                    class="btn-secondary"
                  >
                    Skip
                  </button>
                </div>
              </div>

              <!-- Answer Display -->
              <div v-else class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Your Answer</label>
                  <div class="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <p class="text-gray-900 whitespace-pre-line">{{ currentQuestion.answer.answer_text }}</p>
                  </div>
                </div>

                <!-- Scores -->
                <div v-if="currentQuestion.answer.scores_json" class="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div
                    v-for="(score, key) in currentQuestion.answer.scores_json"
                    :key="key"
                    class="p-3 bg-gray-50 rounded-lg"
                  >
                    <div class="text-xs text-gray-600 mb-1">{{ key }}</div>
                    <div class="text-lg font-semibold text-gray-900">{{ score }}/10</div>
                  </div>
                </div>

                <!-- Feedback -->
                <div v-if="currentQuestion.answer.feedback_json" class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h3 class="font-medium text-blue-900 mb-2">Feedback</h3>
                  <p class="text-blue-800 whitespace-pre-line">
                    <template v-if="typeof currentQuestion.answer.feedback_json === 'string'">
                      {{ currentQuestion.answer.feedback_json }}
                    </template>
                    <template v-else>
                      <p v-if="currentQuestion.answer.feedback_json.strengths">
                        <strong>Strengths:</strong> {{ currentQuestion.answer.feedback_json.strengths }}
                      </p>
                      <p v-if="currentQuestion.answer.feedback_json.weaknesses">
                        <strong>Weaknesses:</strong> {{ currentQuestion.answer.feedback_json.weaknesses }}
                      </p>
                      <p v-if="currentQuestion.answer.feedback_json.improvements">
                        <strong>Improvements:</strong> {{ currentQuestion.answer.feedback_json.improvements }}
                      </p>
                    </template>
                  </p>
                </div>

                <!-- Navigation -->
                <div class="flex gap-4 pt-4">
                  <button
                    v-if="currentQuestionIndex > 0"
                    @click="previousQuestion"
                    class="btn-secondary"
                  >
                    Previous
                  </button>
                  <button
                    v-if="currentQuestionIndex < interviewStore.questions.length - 1"
                    @click="nextQuestion"
                    class="btn-primary"
                  >
                    Next Question
                  </button>
                  <button
                    v-else
                    @click="handleFinishInterview"
                    :disabled="interviewStore.isLoading"
                    class="btn-primary"
                  >
                    {{ interviewStore.isLoading ? 'Finishing...' : 'Finish Interview' }}
                  </button>
                </div>
              </div>
            </div>
          </Card>

          <!-- Error Message -->
          <div v-if="interviewStore.error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {{ interviewStore.error }}
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interviews'
import Card from '../components/Card.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()

const answerText = ref('')
const startTime = ref(null)

const currentQuestionIndex = computed(() => interviewStore.currentQuestionIndex)
const currentQuestion = computed(() => {
  return interviewStore.questions[currentQuestionIndex.value] || null
})

const progress = computed(() => {
  return interviewStore.currentSession?.progress || { current_question: 0, total_questions: 0 }
})

const progressPercentage = computed(() => {
  if (!progress.value.total_questions) return 0
  return (progress.value.current_question / progress.value.total_questions) * 100
})

async function handleSubmitAnswer() {
  if (!answerText.value.trim() || !currentQuestion.value) return

  const timeSeconds = startTime.value ? Math.floor((Date.now() - startTime.value) / 1000) : 0

  try {
    await interviewStore.submitAnswer(route.params.id, {
      question_id: currentQuestion.value.id,
      answer_text: answerText.value.trim(),
      time_seconds: timeSeconds,
    })
    answerText.value = ''
    startTime.value = null
  } catch (err) {
    // Error handled by store
  }
}

function nextQuestion() {
  if (currentQuestionIndex.value < interviewStore.questions.length - 1) {
    interviewStore.setCurrentQuestionIndex(currentQuestionIndex.value + 1)
    answerText.value = ''
    startTime.value = Date.now()
  }
}

function previousQuestion() {
  if (currentQuestionIndex.value > 0) {
    interviewStore.setCurrentQuestionIndex(currentQuestionIndex.value - 1)
    answerText.value = ''
    startTime.value = Date.now()
  }
}

function skipQuestion() {
  nextQuestion()
}

async function handleFinishInterview() {
  try {
    await interviewStore.finishSession(route.params.id)
    setTimeout(() => {
      router.push('/dashboard')
    }, 1000)
  } catch (err) {
    // Error handled by store
  }
}

onMounted(async () => {
  const sessionId = route.params.id
  try {
    await interviewStore.fetchSession(sessionId)
    await interviewStore.fetchQuestions(sessionId)
    startTime.value = Date.now()
  } catch (err) {
    // Error handled by store
  }
})

// Reset answer text when question changes
watch(currentQuestionIndex, () => {
  answerText.value = ''
  startTime.value = Date.now()
})
</script>
