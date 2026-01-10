"""
CV extraction service using LLM (OpenAI or Anthropic).
Extracts structured profile data from CV text with high accuracy.
"""
import json
import re
from typing import Dict
from django.conf import settings


def extract_profile_data(cv_text: str) -> Dict:
    """
    Extract profile data from CV text using LLM.
    
    Args:
        cv_text: Extracted CV text
        
    Returns:
        Dictionary with keys: experience, skills, education, projects
    """
    # Check OpenAI API key
    openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    
    if not openai_key:
        raise ValueError(
            "OPENAI_API_KEY not configured. Please set OPENAI_API_KEY in .env file and restart the server."
        )
    
    return _extract_with_openai(cv_text)


def _extract_with_openai(cv_text: str) -> Dict:
    """Extract profile data using OpenAI API."""
    try:
        import openai
    except ImportError:
        raise ImportError("openai package is required. Install with: pip install openai")
    
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured in settings")
    
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""Extract structured information from the following CV/resume text. Return ONLY a valid JSON object with the following structure:

{{
  "primary_role": "Primary Job Title/Role",  // The main role/title based on experience (e.g., "Marketing Manager", "Sales Engineer", "Data Analyst", "Software Engineer")
  "role_category": "category",  // Field/domain: "it", "marketing", "sales", "finance", "hr", "design", "data", "product", "operations", "other"
  "skills": ["skill1", "skill2", ...],  // List of individual technical skills and languages. Split concatenated skills (e.g., "Python JWT" -> ["Python", "JWT"], "Django HTML/CSS" -> ["Django", "HTML", "CSS"]). Normalize aliases (e.g., "DRF" -> "Django REST Framework").
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "dates": "Date range",
      "description": ["bullet point 1", "bullet point 2", ...]  // List of responsibilities/achievements
    }}
  ],
  "education": [
    {{
      "degree": "Degree name",
      "institution": "Institution name",
      "dates": "Date range or year"
    }}
  ],
  "projects": [
    {{
      "name": "Project name",
      "description": "Project description",
      "technologies": ["tech1", "tech2", ...],  // List of technologies used
      "dates": "Date range if available"
    }}
  ]
}}

Important rules:
- Split concatenated skills properly (e.g., "Python JWT" -> ["Python", "JWT"])
- For experience: Only include actual job positions with title and company. Do NOT include bullet points or descriptions as separate entries.
- For education: Only include complete entries. Skip incomplete abbreviations.
- For projects: Extract technologies separately from description.

CV Text:
{cv_text[:8000]}  # Limit to avoid token limits
"""

    try:
        response = client.chat.completions.create(
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-4'),
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at extracting structured data from CVs and resumes. Always return valid JSON only."
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
        
        # Ensure all required keys exist
        return {
            'primary_role': data.get('primary_role', ''),
            'role_category': data.get('role_category', 'other'),
            'skills': data.get('skills', []),
            'experience': data.get('experience', []),
            'education': data.get('education', []),
            'projects': data.get('projects', []),
        }
        
    except Exception as e:
        error_str = str(e)
        # Provide more helpful error messages
        if '429' in error_str or 'insufficient_quota' in error_str.lower():
            raise RuntimeError(
                f"OpenAI quota exceeded. Please check your billing at https://platform.openai.com/account/billing "
                f"or add ANTHROPIC_API_KEY to .env as an alternative. Original error: {error_str}"
            )
        elif '401' in error_str or 'invalid_api_key' in error_str.lower():
            raise RuntimeError(
                f"Invalid OpenAI API key. Please check your OPENAI_API_KEY in .env file. Original error: {error_str}"
            )
        else:
            raise RuntimeError(f"OpenAI extraction failed: {error_str}")


