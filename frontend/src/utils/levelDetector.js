/**
 * Determines the experience level (junior, mid, senior) based on profile data.
 * 
 * @param {Object} profileData - The profile data_json object
 * @returns {string|null} - 'junior', 'mid', 'senior', or null if insufficient data
 */
export function determineLevel(profileData) {
  if (!profileData) {
    return null
  }

  const experience = profileData.experience || []
  const skills = profileData.skills || []
  
  // Calculate years of experience from dates
  let totalYears = 0
  const currentYear = new Date().getFullYear()
  
  experience.forEach(exp => {
    if (exp.dates) {
      const dateStr = exp.dates.toLowerCase()
      const years = dateStr.match(/\b(19|20)\d{2}\b/g)
      
      if (years && years.length >= 1) {
        const startYear = parseInt(years[0])
        const endYear = years.length >= 2 ? parseInt(years[1]) : currentYear
        
        if (startYear && endYear) {
          const yearsDiff = Math.max(0, endYear - startYear)
          totalYears += yearsDiff
        }
      }
    }
  })
  
  // Check job titles for level indicators
  const titleKeywords = {
    senior: ['senior', 'lead', 'principal', 'architect', 'manager', 'director', 'head', 'chief'],
    mid: ['mid', 'intermediate', 'specialist', 'engineer', 'developer'],
    junior: ['junior', 'entry', 'intern', 'associate', 'trainee', 'graduate']
  }
  
  let titleLevel = null
  experience.forEach(exp => {
    if (exp.title) {
      const titleLower = exp.title.toLowerCase()
      
      if (titleKeywords.senior.some(keyword => titleLower.includes(keyword))) {
        titleLevel = 'senior'
      } else if (!titleLevel && titleKeywords.junior.some(keyword => titleLower.includes(keyword))) {
        titleLevel = 'junior'
      } else if (!titleLevel && titleKeywords.mid.some(keyword => titleLower.includes(keyword))) {
        titleLevel = 'mid'
      }
    }
  })
  
  // If no experience data at all, return null
  if (experience.length === 0 && totalYears === 0) {
    return null
  }
  
  // Determine level based on years of experience
  let yearsLevel = 'junior'
  if (totalYears >= 5) {
    yearsLevel = 'senior'
  } else if (totalYears >= 2) {
    yearsLevel = 'mid'
  }
  
  // Combine title and years - title takes precedence if it suggests higher level
  if (titleLevel === 'senior') {
    return 'senior'
  } else if (titleLevel === 'junior' && totalYears < 2) {
    return 'junior'
  } else if (yearsLevel === 'senior' || (titleLevel === null && totalYears >= 5)) {
    return 'senior'
  } else if (yearsLevel === 'mid' || (titleLevel === null && totalYears >= 2)) {
    return 'mid'
  }
  
  return 'junior'
}

/**
 * Gets a human-readable description of the detected level.
 */
export function getLevelDescription(level) {
  const descriptions = {
    junior: 'Entry level (0-2 years)',
    mid: 'Mid-level (2-5 years)',
    senior: 'Senior (5+ years)'
  }
  return descriptions[level] || 'Unknown Level'
}

