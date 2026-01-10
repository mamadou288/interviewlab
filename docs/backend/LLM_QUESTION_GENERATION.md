# LLM-Based Question Generation

## Overview

The interview question generation system can use Large Language Models (LLMs) to create **personalized, tailored interview questions** based on:

- **Role**: The specific position (Backend Engineer, Frontend Developer, etc.)
- **Level**: Junior, Mid-level, or Senior
- **Interview Type**: HR, Technical, Case Study, or Mixed
- **Candidate's CV**: Extracted skills, experience, education, projects
- **CV Text**: Full extracted text from the uploaded CV

## How It Works

### 1. LLM Integration

The system supports two LLM providers:
- **OpenAI** (GPT-4)
- **Anthropic** (Claude)

### 2. Question Generation Flow

```
Interview Session Created
    ↓
Check if LLM is enabled (USE_LLM_FOR_QUESTIONS)
    ↓
If enabled:
    → Build context (role, level, CV, skills, experience)
    → Send prompt to LLM
    → Parse LLM response (JSON)
    → Create InterviewQuestion objects
    ↓
If disabled or LLM fails:
    → Fallback to hardcoded questions
```

### 3. Context Building

The LLM receives comprehensive context:

```json
{
  "role": {
    "name": "Backend Engineer",
    "category": "backend",
    "description": "...",
    "keywords": ["python", "django", "api", ...],
    "level_keywords": ["optimization", "scalability", ...]
  },
  "level": "mid",
  "interview_type": "technical",
  "candidate": {
    "skills": ["Python", "Django", "PostgreSQL"],
    "experience": [...],
    "projects": [...]
  },
  "cv_text": "Extracted CV text..."
}
```

### 4. Personalized Questions

The LLM generates questions that:
- Reference the candidate's specific skills
- Relate to their experience and projects
- Match the role requirements
- Are appropriate for their level
- Assess both technical knowledge and practical experience

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# Enable LLM question generation
USE_LLM_FOR_QUESTIONS=True

# Choose LLM provider
LLM_PROVIDER=openai  # or 'anthropic'

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo

# Anthropic Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### Installation

Install required packages:

```bash
pip install openai>=1.0.0
pip install anthropic>=0.18.0
```

## Fallback Behavior

If LLM generation fails (API error, no key configured, etc.), the system automatically falls back to the hardcoded question generator. This ensures interviews can always be created.

## Example Generated Questions

With LLM enabled, questions might look like:

**Instead of generic:**
> "Explain how REST APIs work."

**Personalized:**
> "Based on your experience building Django REST APIs for e-commerce platforms, explain how you would design an API endpoint for handling concurrent order processing with proper error handling and transaction management."

This makes interviews much more relevant and engaging for candidates!

