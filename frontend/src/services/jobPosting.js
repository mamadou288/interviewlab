import apiClient from './api'

export const jobPostingService = {
  async parseJobPosting(jobPostingText) {
    const response = await apiClient.post('/job-posting/parse', { job_posting_text: jobPostingText })
    return response.data
  },
}

