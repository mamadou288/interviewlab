import { defineStore } from 'pinia'
import { ref } from 'vue'
import { interviewService } from '../services/interviews'

export const useInterviewStore = defineStore('interviews', () => {
  const currentSession = ref(null)
  const questions = ref([])
  const currentQuestionIndex = ref(0)
  const isLoading = ref(false)
  const error = ref(null)

  async function createSession(sessionData) {
    isLoading.value = true
    error.value = null
    try {
      const data = await interviewService.createSession(sessionData)
      currentSession.value = data
      currentQuestionIndex.value = 0
      return data
    } catch (err) {
      error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to create interview session'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSession(id) {
    isLoading.value = true
    error.value = null
    try {
      const data = await interviewService.getSession(id)
      currentSession.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to fetch interview session'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchQuestions(sessionId) {
    isLoading.value = true
    error.value = null
    try {
      const data = await interviewService.getQuestions(sessionId)
      questions.value = data.questions || []
      const firstUnansweredIndex = questions.value.findIndex(q => !q.answer)
      currentQuestionIndex.value = firstUnansweredIndex !== -1 ? firstUnansweredIndex : 0
      return data.questions
    } catch (err) {
      error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to fetch questions'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function submitAnswer(sessionId, answerData) {
    isLoading.value = true
    error.value = null
    try {
      const data = await interviewService.submitAnswer(sessionId, answerData)
      const questionToUpdate = questions.value.find(q => q.id === answerData.question_id)
      if (questionToUpdate) {
        questionToUpdate.answer = data
      }
      await fetchSession(sessionId)
      return data
    } catch (err) {
      error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to submit answer'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function finishSession(sessionId) {
    isLoading.value = true
    error.value = null
    try {
      const data = await interviewService.finishSession(sessionId)
      currentSession.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to finish session'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function setCurrentQuestionIndex(index) {
    if (index >= 0 && index < questions.value.length) {
      currentQuestionIndex.value = index
    }
  }

  return {
    currentSession,
    questions,
    currentQuestionIndex,
    isLoading,
    error,
    createSession,
    fetchSession,
    fetchQuestions,
    submitAnswer,
    finishSession,
    setCurrentQuestionIndex,
  }
})

