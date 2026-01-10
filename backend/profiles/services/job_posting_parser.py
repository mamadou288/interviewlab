"""
Job posting parser service using LLM.
Extracts structured information from job posting text.
"""
import json
from typing import Dict
from django.conf import settings


def parse_job_posting(job_text: str) -> Dict:
    """
    Parse job posting text and extract structured information.
    
    Args:
        job_text: Job posting text
        
    Returns:
        Dictionary with keys: role_name, level, required_skills, preferred_skills, 
        experience_years, job_type, description
    """
    try:
        import openai
    except ImportError:
        raise ImportError("openai package is required. Install with: pip install openai")
    
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured in settings")
    
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""Extract structured information from the following job posting. Return ONLY a valid JSON object with the following structure:

{{
  "role_name": "Job Title/Role Name",  // e.g., "Senior Backend Engineer", "Frontend Developer"
  "level": "junior" | "mid" | "senior",  // Experience level required
  "required_skills": ["skill1", "skill2", ...],  // Must-have skills
  "preferred_skills": ["skill1", "skill2", ...],  // Nice-to-have skills
  "experience_years": number,  // Minimum years of experience required (0 if not specified)
  "job_type": "full-time" | "part-time" | "contract" | "internship" | "not specified",
  "description": "Brief summary of the role",
  "location": "Location if mentioned",
  "company": "Company name if mentioned"
}}

Important rules:
- Determine level based on job title keywords (senior, lead, principal = senior; junior, entry, intern = junior; otherwise mid)
- Extract all technical skills mentioned (programming languages, frameworks, tools)
- If experience years are mentioned (e.g., "3+ years", "5 years experience"), extract the number
- If no level can be determined, default to "mid"

Job Posting Text:
{job_text[:8000]}  # Limit to avoid token limits
"""

    try:
        response = client.chat.completions.create(
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-4'),
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at parsing job postings and extracting structured information. Always return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent extraction
            response_format={"type": "json_object"}  # Force JSON response
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Normalize level
        level = data.get('level', 'mid').lower()
        if level not in ['junior', 'mid', 'senior']:
            # Try to infer from role_name
            role_name_lower = data.get('role_name', '').lower()
            if any(keyword in role_name_lower for keyword in ['senior', 'lead', 'principal', 'architect', 'manager']):
                level = 'senior'
            elif any(keyword in role_name_lower for keyword in ['junior', 'entry', 'intern', 'associate']):
                level = 'junior'
            else:
                level = 'mid'
        
        return {
            'role_name': data.get('role_name', ''),
            'level': level,
            'required_skills': data.get('required_skills', []),
            'preferred_skills': data.get('preferred_skills', []),
            'experience_years': data.get('experience_years', 0),
            'job_type': data.get('job_type', 'not specified'),
            'description': data.get('description', ''),
            'location': data.get('location', ''),
            'company': data.get('company', ''),
        }
        
    except Exception as e:
        error_str = str(e)
        if '429' in error_str or 'insufficient_quota' in error_str.lower():
            raise RuntimeError(
                f"OpenAI quota exceeded. Please check your billing at https://platform.openai.com/account/billing. Original error: {error_str}"
            )
        elif '401' in error_str or 'invalid_api_key' in error_str.lower():
            raise RuntimeError(
                f"Invalid OpenAI API key. Please check your OPENAI_API_KEY in .env file. Original error: {error_str}"
            )
        else:
            raise RuntimeError(f"OpenAI parsing failed: {error_str}")

