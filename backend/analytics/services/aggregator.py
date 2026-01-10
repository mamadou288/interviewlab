from typing import Dict, List
from django.contrib.auth import get_user_model
from interviews.models import InterviewSession
from interviews.services.report import generate_report

User = get_user_model()


def get_session_stats(user) -> Dict:
    """
    Returns session-level stats for a user.
    
    Args:
        user: User instance
        
    Returns:
        Dictionary with total_sessions, completed_sessions, average_score
    """
    all_sessions = InterviewSession.objects.filter(user=user)
    completed_sessions = all_sessions.filter(status='completed')
    
    total_sessions = all_sessions.count()
    completed_count = completed_sessions.count()
    
    # Calculate average score from completed sessions
    scores = [s.overall_score for s in completed_sessions if s.overall_score is not None]
    average_score = round(sum(scores) / len(scores), 2) if scores else 0.0
    
    return {
        'total_sessions': total_sessions,
        'completed_sessions': completed_count,
        'average_score': average_score,
    }


def get_progress_stats(user) -> Dict:
    """
    Returns progress over time stats.
    
    Args:
        user: User instance
        
    Returns:
        Dictionary with score trends and category trends
    """
    completed_sessions = InterviewSession.objects.filter(
        user=user,
        status='completed'
    ).order_by('ended_at', 'started_at')
    
    return {
        'sessions': completed_sessions,
    }


def get_skill_map_stats(user) -> Dict:
    """
    Returns skill coverage and mastery data.
    
    Args:
        user: User instance
        
    Returns:
        Dictionary with skill coverage and mastery information
    """
    completed_sessions = InterviewSession.objects.filter(
        user=user,
        status='completed'
    )
    
    # Collect all skill tags from all sessions
    all_skills = {}
    
    for session in completed_sessions:
        report = generate_report(str(session.id))
        if report and 'skill_breakdown' in report:
            skill_breakdown = report['skill_breakdown']
            for skill_tag, score in skill_breakdown.items():
                if skill_tag not in all_skills:
                    all_skills[skill_tag] = {
                        'scores': [],
                        'sessions': [],
                    }
                all_skills[skill_tag]['scores'].append(score)
                all_skills[skill_tag]['sessions'].append(session)
    
    # Calculate mastery (rolling average) for each skill
    skill_mastery = {}
    for skill_tag, data in all_skills.items():
        if data['scores']:
            # Simple average for now (can be weighted by recency later)
            mastery = round(sum(data['scores']) / len(data['scores']), 2)
            skill_mastery[skill_tag] = {
                'mastery': mastery,
                'attempts': len(data['scores']),
                'last_practiced': max([s.ended_at or s.started_at for s in data['sessions']]),
            }
    
    return {
        'skill_mastery': skill_mastery,
        'total_skills': len(skill_mastery),
    }


def get_interview_realism_stats(user) -> Dict:
    """
    Returns follow-up and pressure scores (optional for MVP).
    
    Args:
        user: User instance
        
    Returns:
        Dictionary with follow-up handling and pressure scores
    """
    completed_sessions = InterviewSession.objects.filter(
        user=user,
        status='completed'
    )
    
    followup_scores = []
    pressure_scores = []
    
    for session in completed_sessions:
        # Get answers with follow-up questions
        from interviews.models import InterviewAnswer, InterviewQuestion
        
        followup_questions = InterviewQuestion.objects.filter(
            session=session,
            is_followup=True
        )
        
        for question in followup_questions:
            try:
                answer = question.answer
                scores = answer.scores_json or {}
                if scores:
                    avg_score = sum(scores.values()) / len(scores)
                    followup_scores.append(avg_score)
            except InterviewAnswer.DoesNotExist:
                pass
        
        # Get answers to hard questions (pressure)
        hard_questions = InterviewQuestion.objects.filter(
            session=session,
            difficulty='hard'
        )
        
        for question in hard_questions:
            try:
                answer = question.answer
                scores = answer.scores_json or {}
                if 'depth' in scores:
                    pressure_scores.append(scores['depth'])
            except InterviewAnswer.DoesNotExist:
                pass
    
    return {
        'followup_handling_score': round(sum(followup_scores) / len(followup_scores), 2) if followup_scores else 0.0,
        'pressure_score': round(sum(pressure_scores) / len(pressure_scores), 2) if pressure_scores else 0.0,
    }

