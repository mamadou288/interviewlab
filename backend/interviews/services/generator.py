import random
from typing import List, Dict
from django.conf import settings
from roles.models import RoleCatalog
from ..models import InterviewSession, InterviewQuestion


def select_questions(role: RoleCatalog, level: str, type: str, profile_data: Dict = None) -> List[Dict]:
    """
    Select questions from question bank based on role, level, and type.
    
    Args:
        role: RoleCatalog instance
        level: 'junior', 'mid', or 'senior'
        type: 'hr', 'technical', 'case', or 'mixed'
        profile_data: Optional profile data for customization
        
    Returns:
        List of question dictionaries
    """
    # Import QuestionBank model (will be created as a fixture)
    # For now, we'll use a simple approach with predefined questions
    # In production, this would query a QuestionBank model
    
    # This is a placeholder - actual implementation will load from fixtures/database
    # For MVP, we'll generate questions programmatically based on role and type
    
    questions = []
    
    # Base questions that can be customized
    base_questions = _get_base_questions(role, level, type)
    
    # Select 10-15 questions with proper distribution
    questions = _distribute_questions(base_questions, type)
    
    return questions[:15]  # Limit to 15 questions


def _get_base_questions(role: RoleCatalog, level: str, type: str) -> List[Dict]:
    """
    Get base questions based on role category and type.
    This is a simplified version - in production, load from QuestionBank model.
    """
    questions = []
    
    # HR Questions
    if type in ['hr', 'mixed']:
        hr_questions = [
            {
                'question_text': 'Tell me about yourself.',
                'category': 'behavioral',
                'difficulty': 'easy',
                'skill_tags': ['communication.star']
            },
            {
                'question_text': 'Describe a time when you had to work under pressure.',
                'category': 'behavioral',
                'difficulty': 'medium',
                'skill_tags': ['communication.star', 'behavioral.pressure']
            },
            {
                'question_text': 'Tell me about a challenging project you worked on.',
                'category': 'behavioral',
                'difficulty': 'medium',
                'skill_tags': ['communication.star', 'behavioral.challenge']
            },
            {
                'question_text': 'How do you handle conflicts in a team?',
                'category': 'behavioral',
                'difficulty': 'medium',
                'skill_tags': ['communication.star', 'behavioral.conflict']
            },
            {
                'question_text': 'What are your strengths and weaknesses?',
                'category': 'behavioral',
                'difficulty': 'easy',
                'skill_tags': ['communication.star']
            },
        ]
        questions.extend(hr_questions)
    
    # Technical Questions (role-specific)
    if type in ['technical', 'mixed']:
        tech_questions = _get_technical_questions(role, level)
        questions.extend(tech_questions)
    
    # Case Study Questions
    if type in ['case', 'mixed']:
        case_questions = [
            {
                'question_text': 'Design a URL shortening service like bit.ly.',
                'category': 'case',
                'difficulty': 'hard',
                'skill_tags': ['system_design.scaling', 'system_design.architecture']
            },
            {
                'question_text': 'How would you design a notification system for a social media app?',
                'category': 'case',
                'difficulty': 'hard',
                'skill_tags': ['system_design.scaling', 'system_design.real_time']
            },
        ]
        questions.extend(case_questions)
    
    return questions


def _get_technical_questions(role: RoleCatalog, level: str) -> List[Dict]:
    """Get technical questions based on role category."""
    questions = []
    
    category = role.category
    
    if category == 'backend':
        questions.extend([
            {
                'question_text': 'Explain how REST APIs work.',
                'category': 'technical',
                'difficulty': 'easy' if level == 'junior' else 'medium',
                'skill_tags': ['backend.api.rest']
            },
            {
                'question_text': 'What is the difference between SQL and NoSQL databases?',
                'category': 'technical',
                'difficulty': 'medium',
                'skill_tags': ['backend.database']
            },
            {
                'question_text': 'Explain authentication and authorization.',
                'category': 'technical',
                'difficulty': 'medium',
                'skill_tags': ['backend.auth']
            },
            {
                'question_text': 'How do you handle database migrations?',
                'category': 'technical',
                'difficulty': 'medium',
                'skill_tags': ['backend.database.migrations']
            },
            {
                'question_text': 'Explain microservices architecture.',
                'category': 'technical',
                'difficulty': 'hard',
                'skill_tags': ['backend.architecture.microservices']
            },
        ])
    elif category == 'frontend':
        questions.extend([
            {
                'question_text': 'Explain the difference between let, const, and var in JavaScript.',
                'category': 'technical',
                'difficulty': 'easy',
                'skill_tags': ['frontend.javascript']
            },
            {
                'question_text': 'What is React and how does it work?',
                'category': 'technical',
                'difficulty': 'medium',
                'skill_tags': ['frontend.react']
            },
            {
                'question_text': 'Explain the virtual DOM concept.',
                'category': 'technical',
                'difficulty': 'medium',
                'skill_tags': ['frontend.react.virtual_dom']
            },
            {
                'question_text': 'How do you optimize frontend performance?',
                'category': 'technical',
                'difficulty': 'hard',
                'skill_tags': ['frontend.performance']
            },
        ])
    elif category == 'fullstack':
        questions.extend([
            {
                'question_text': 'Explain the full-stack development workflow.',
                'category': 'technical',
                'difficulty': 'medium',
                'skill_tags': ['fullstack.workflow']
            },
            {
                'question_text': 'How do you handle state management in a full-stack application?',
                'category': 'technical',
                'difficulty': 'hard',
                'skill_tags': ['fullstack.state_management']
            },
        ])
    
    # Adjust difficulty based on level
    for q in questions:
        if level == 'junior' and q['difficulty'] == 'hard':
            q['difficulty'] = 'medium'
        elif level == 'senior' and q['difficulty'] == 'easy':
            q['difficulty'] = 'medium'
    
    return questions


def _distribute_questions(questions: List[Dict], type: str) -> List[Dict]:
    """
    Ensure proper question distribution based on interview type.
    
    Args:
        questions: List of question dicts
        type: Interview type
        
    Returns:
        Distributed list of questions
    """
    if type == 'hr':
        # 40% behavioral, 30% situational, 30% role-specific
        behavioral = [q for q in questions if q['category'] == 'behavioral']
        technical = [q for q in questions if q['category'] == 'technical']
        
        selected = []
        selected.extend(behavioral[:4])  # 40%
        selected.extend(technical[:3])   # 30%
        # Add more behavioral if needed
        if len(selected) < 10:
            selected.extend(behavioral[4:])
        
        return selected[:10]
    
    elif type == 'technical':
        # 50% core, 30% advanced, 20% practical
        technical = [q for q in questions if q['category'] == 'technical']
        easy_medium = [q for q in technical if q['difficulty'] in ['easy', 'medium']]
        hard = [q for q in technical if q['difficulty'] == 'hard']
        
        selected = []
        selected.extend(easy_medium[:5])  # 50%
        selected.extend(hard[:3])          # 30%
        # Fill remaining with medium
        if len(selected) < 10:
            selected.extend(easy_medium[5:])
        
        return selected[:10]
    
    elif type == 'case':
        # 60% problem-solving, 40% system design
        case = [q for q in questions if q['category'] == 'case']
        technical = [q for q in questions if q['category'] == 'technical']
        
        selected = []
        selected.extend(case[:6])      # 60%
        selected.extend(technical[:4]) # 40%
        
        return selected[:10]
    
    else:  # mixed
        # Balanced distribution
        behavioral = [q for q in questions if q['category'] == 'behavioral']
        technical = [q for q in questions if q['category'] == 'technical']
        case = [q for q in questions if q['category'] == 'case']
        
        selected = []
        selected.extend(behavioral[:3])
        selected.extend(technical[:4])
        selected.extend(case[:3])
        
        return selected[:10]


def assign_skill_tags(questions: List[Dict], role: RoleCatalog) -> List[Dict]:
    """
    Assign relevant skill tags to questions based on role.
    
    Args:
        questions: List of question dicts
        role: RoleCatalog instance
        
    Returns:
        Questions with assigned skill tags
    """
    role_keywords = [kw.lower() for kw in role.keywords_json if isinstance(kw, str)]
    
    for question in questions:
        # If question doesn't have skill tags, assign based on role
        if not question.get('skill_tags'):
            # Map role category to skill tags
            if role.category == 'backend':
                question['skill_tags'] = ['backend.general']
            elif role.category == 'frontend':
                question['skill_tags'] = ['frontend.general']
            elif role.category == 'fullstack':
                question['skill_tags'] = ['fullstack.general']
            else:
                question['skill_tags'] = [f"{role.category}.general"]
    
    return questions


def generate_interview_questions(session_id: str) -> List[InterviewQuestion]:
    """
    Main function that generates questions for an interview session.
    Uses LLM if configured, otherwise falls back to hardcoded questions.
    
    Args:
        session_id: UUID of InterviewSession
        
    Returns:
        List of InterviewQuestion objects
    """
    try:
        session = InterviewSession.objects.get(id=session_id)
    except InterviewSession.DoesNotExist:
        return []
    
    # Try to use LLM for question generation
    use_llm = getattr(settings, 'USE_LLM_FOR_QUESTIONS', False)
    
    if use_llm:
        try:
            from .llm_generator import generate_questions_with_llm
            
            # Get CV document if available
            cv_document = None
            if session.profile and session.profile.cv_document:
                cv_document = session.profile.cv_document
            
            # Generate questions using LLM
            question_dicts = generate_questions_with_llm(
                role=session.role_selected,
                level=session.level,
                interview_type=session.type,
                profile=session.profile,
                cv_document=cv_document
            )
            
            # If LLM returned questions, use them
            if question_dicts:
                # Create InterviewQuestion objects
                questions = []
                for idx, q_dict in enumerate(question_dicts, start=1):
                    question = InterviewQuestion.objects.create(
                        session=session,
                        order=idx,
                        question_text=q_dict['question_text'],
                        category=q_dict.get('category', 'technical'),
                        difficulty=q_dict.get('difficulty', 'medium'),
                        skill_tags_json=q_dict.get('skill_tags', [])
                    )
                    questions.append(question)
                
                return questions
        except Exception as e:
            # Log error but continue with fallback
            pass
    
    # Fallback to hardcoded questions
    profile_data = None
    if session.profile:
        profile_data = session.profile.data_json
    
    # Select questions using hardcoded generator
    question_dicts = select_questions(
        session.role_selected,
        session.level,
        session.type,
        profile_data
    )
    
    # Assign skill tags
    question_dicts = assign_skill_tags(question_dicts, session.role_selected)
    
    # Create InterviewQuestion objects
    questions = []
    for idx, q_dict in enumerate(question_dicts, start=1):
        question = InterviewQuestion.objects.create(
            session=session,
            order=idx,
            question_text=q_dict['question_text'],
            category=q_dict['category'],
            difficulty=q_dict['difficulty'],
            skill_tags_json=q_dict.get('skill_tags', [])
        )
        questions.append(question)
    
    return questions

