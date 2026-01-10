"""
LLM-based question generation service.
Uses OpenAI or Anthropic to generate personalized interview questions.
"""
import os
import json
from typing import List, Dict, Optional
from django.conf import settings
from roles.models import RoleCatalog
from profiles.models import Profile, CVDocument


def generate_questions_with_llm(
    role: RoleCatalog,
    level: str,
    interview_type: str,
    profile: Optional[Profile] = None,
    cv_document: Optional[CVDocument] = None
) -> List[Dict]:
    """
    Generate personalized interview questions using LLM.
    
    Args:
        role: RoleCatalog instance
        level: 'junior', 'mid', or 'senior'
        interview_type: 'hr', 'technical', 'case', or 'mixed'
        profile: Optional Profile instance with extracted data
        cv_document: Optional CVDocument instance
        
    Returns:
        List of question dictionaries
    """
    # Check if LLM is configured
    llm_provider = getattr(settings, 'LLM_PROVIDER', 'openai').lower()
    
    if llm_provider == 'openai':
        return _generate_with_openai(role, level, interview_type, profile, cv_document)
    elif llm_provider == 'anthropic':
        return _generate_with_anthropic(role, level, interview_type, profile, cv_document)
    else:
        # Fallback to hardcoded questions if no LLM configured
        from .generator import select_questions
        profile_data = profile.data_json if profile else {}
        return select_questions(role, level, interview_type, profile_data)


def _generate_with_openai(
    role: RoleCatalog,
    level: str,
    interview_type: str,
    profile: Optional[Profile] = None,
    cv_document: Optional[CVDocument] = None
) -> List[Dict]:
    """Generate questions using OpenAI API."""
    try:
        import openai
    except ImportError:
        raise ImportError("openai package is required. Install with: pip install openai")
    
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured in settings")
    
    client = openai.OpenAI(api_key=api_key)
    
    # Build context for the LLM
    context = _build_context(role, level, interview_type, profile, cv_document)
    
    # Create the prompt
    prompt = _create_question_generation_prompt(context, interview_type)
    
    try:
        response = client.chat.completions.create(
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-4'),
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical interviewer who creates personalized, relevant interview questions based on candidate profiles, roles, and experience levels."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse the response
        content = response.choices[0].message.content
        questions = _parse_llm_response(content)
        
        return questions
        
    except Exception as e:
        # Fallback to hardcoded questions on error
        from .generator import select_questions
        profile_data = profile.data_json if profile else {}
        return select_questions(role, level, interview_type, profile_data)


def _generate_with_anthropic(
    role: RoleCatalog,
    level: str,
    interview_type: str,
    profile: Optional[Profile] = None,
    cv_document: Optional[CVDocument] = None
) -> List[Dict]:
    """Generate questions using Anthropic Claude API."""
    try:
        from anthropic import Anthropic
    except ImportError:
        raise ImportError("anthropic package is required. Install with: pip install anthropic")
    
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not configured in settings")
    
    client = Anthropic(api_key=api_key)
    
    # Build context for the LLM
    context = _build_context(role, level, interview_type, profile, cv_document)
    
    # Create the prompt
    prompt = _create_question_generation_prompt(context, interview_type)
    
    try:
        message = client.messages.create(
            model=getattr(settings, 'ANTHROPIC_MODEL', 'claude-3-sonnet-20240229'),
            max_tokens=2000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": f"You are an expert technical interviewer. {prompt}"
                }
            ]
        )
        
        # Parse the response
        content = message.content[0].text
        questions = _parse_llm_response(content)
        
        return questions
        
    except Exception as e:
        # Fallback to hardcoded questions on error
        from .generator import select_questions
        profile_data = profile.data_json if profile else {}
        return select_questions(role, level, interview_type, profile_data)


def _build_context(
    role: RoleCatalog,
    level: str,
    interview_type: str,
    profile: Optional[Profile] = None,
    cv_document: Optional[CVDocument] = None
) -> Dict:
    """Build context dictionary for LLM prompt."""
    context = {
        'role': {
            'name': role.name,
            'category': role.category,
            'description': role.description,
            'keywords': role.keywords_json,
            'level_keywords': role.level_keywords_json.get(level, []) if isinstance(role.level_keywords_json, dict) else []
        },
        'level': level,
        'interview_type': interview_type,
    }
    
    # Add profile data if available
    if profile and profile.data_json:
        context['candidate'] = {
            'skills': profile.data_json.get('skills', []),
            'experience': profile.data_json.get('experience', []),
            'education': profile.data_json.get('education', []),
            'projects': profile.data_json.get('projects', [])
        }
    
    # Add CV text if available
    if cv_document and cv_document.extracted_text:
        # Limit CV text to avoid token limits (first 2000 chars)
        context['cv_text'] = cv_document.extracted_text[:2000]
    
    return context


def _create_question_generation_prompt(context: Dict, interview_type: str) -> str:
    """Create the prompt for LLM question generation."""
    
    role_info = context['role']
    level = context['level']
    candidate_info = context.get('candidate', {})
    cv_text = context.get('cv_text', '')
    
    # Build candidate summary
    candidate_summary = ""
    if candidate_info:
        skills = candidate_info.get('skills', [])
        experience = candidate_info.get('experience', [])
        projects = candidate_info.get('projects', [])
        
        candidate_summary = f"""
Candidate Profile:
- Skills: {', '.join(skills[:10]) if skills else 'Not specified'}
- Experience: {len(experience)} position(s)
- Projects: {len(projects)} project(s)
"""
    
    if cv_text:
        candidate_summary += f"\nCV Excerpt:\n{cv_text[:500]}"
    
    # Determine question distribution
    if interview_type == 'hr':
        distribution = "Focus 60% on behavioral questions, 40% on role-specific questions"
        question_count = 8
    elif interview_type == 'technical':
        distribution = "Focus 70% on technical depth questions, 30% on practical application"
        question_count = 10
    elif interview_type == 'case':
        distribution = "Focus 60% on system design/case studies, 40% on problem-solving"
        question_count = 8
    else:  # mixed
        distribution = "Balance: 30% behavioral, 50% technical, 20% case studies"
        question_count = 12
    
    prompt = f"""Generate {question_count} personalized interview questions for a {level}-level {role_info['name']} position.

Role Details:
- Position: {role_info['name']} ({role_info['category']})
- Description: {role_info['description']}
- Required Skills: {', '.join(role_info['keywords'][:15])}
- Level-specific focus: {', '.join(role_info['level_keywords']) if role_info['level_keywords'] else 'General'}

{candidate_summary}

Requirements:
1. {distribution}
2. Questions should be tailored to the candidate's background (skills, experience, projects)
3. Difficulty should match {level} level
4. Questions should assess both technical knowledge and practical experience
5. Include questions that relate to the candidate's specific skills and projects when possible
6. Make questions specific and actionable, not generic

Return ONLY a valid JSON array of question objects. Each question object should have:
- "question_text": string (the actual question)
- "category": string (one of: "behavioral", "technical", "case")
- "difficulty": string (one of: "easy", "medium", "hard")
- "skill_tags": array of strings (relevant skills being assessed)
- "context": string (optional: why this question is relevant for this candidate)

Example format:
[
  {{
    "question_text": "Based on your experience with Python and Django, explain how you would design a REST API for a task management system.",
    "category": "technical",
    "difficulty": "medium",
    "skill_tags": ["backend.api.rest", "python", "django"],
    "context": "Tailored to candidate's Python/Django skills"
  }},
  ...
]

Generate {question_count} questions now:"""
    
    return prompt


def _parse_llm_response(content: str) -> List[Dict]:
    """Parse LLM response and extract questions."""
    try:
        # Try to extract JSON from the response
        # LLM might wrap JSON in markdown code blocks
        content = content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        content = content.strip()
        
        # Parse JSON
        questions = json.loads(content)
        
        # Validate and normalize questions
        normalized_questions = []
        for q in questions:
            if isinstance(q, dict) and 'question_text' in q:
                normalized_questions.append({
                    'question_text': q['question_text'],
                    'category': q.get('category', 'technical'),
                    'difficulty': q.get('difficulty', 'medium'),
                    'skill_tags': q.get('skill_tags', []),
                })
        
        return normalized_questions[:15]  # Limit to 15 questions
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # Return empty list, will fallback to hardcoded questions
        return []

