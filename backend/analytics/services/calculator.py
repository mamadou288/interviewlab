from typing import Dict, List
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from interviews.models import InterviewSession
from interviews.services.report import generate_report

User = get_user_model()


def calculate_score_trend(sessions: List[InterviewSession]) -> List[Dict]:
    """
    Calculate score trend over time for line chart data.
    
    Args:
        sessions: List of InterviewSession instances (should be ordered by date)
        
    Returns:
        List of dictionaries with date and score: [{"date": "YYYY-MM-DD", "score": int}, ...]
    """
    trend_data = []
    
    for session in sessions:
        if session.overall_score is not None:
            # Use ended_at if available, otherwise started_at
            date = session.ended_at or session.started_at
            trend_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'score': session.overall_score,
            })
    
    return trend_data


def calculate_category_trend(sessions: List[InterviewSession]) -> Dict:
    """
    Calculate average scores by interview type.
    
    Args:
        sessions: List of InterviewSession instances
        
    Returns:
        Dictionary with average scores by type: {"hr": float, "technical": float, "case": float, "mixed": float}
    """
    category_scores = {
        'hr': [],
        'technical': [],
        'case': [],
        'mixed': [],
    }
    
    for session in sessions:
        if session.overall_score is not None:
            session_type = session.type
            if session_type in category_scores:
                category_scores[session_type].append(session.overall_score)
    
    category_trend = {}
    for category, scores in category_scores.items():
        if scores:
            category_trend[category] = round(sum(scores) / len(scores), 2)
        else:
            category_trend[category] = 0.0
    
    return category_trend


def calculate_skill_mastery(user, skill_tag: str) -> float:
    """
    Calculate rolling average score for a skill (weighted by recency).
    
    Args:
        user: User instance
        skill_tag: Skill tag string (e.g., "communication.star")
        
    Returns:
        Rolling average score (0-5 scale)
    """
    completed_sessions = InterviewSession.objects.filter(
        user=user,
        status='completed'
    ).order_by('-ended_at', '-started_at')
    
    skill_scores = []
    
    for session in completed_sessions:
        report = generate_report(str(session.id))
        if report and 'skill_breakdown' in report:
            skill_breakdown = report['skill_breakdown']
            if skill_tag in skill_breakdown:
                skill_scores.append(skill_breakdown[skill_tag])
    
    if not skill_scores:
        return 0.0
    
    # Weight recent scores more heavily
    if len(skill_scores) == 1:
        return round(skill_scores[0], 2)
    
    # Simple weighted average: recent scores get higher weight
    weights = []
    for i in range(len(skill_scores)):
        # More recent = higher weight (linear weighting)
        weight = (i + 1) / len(skill_scores)
        weights.append(weight)
    
    weighted_sum = sum(score * weight for score, weight in zip(skill_scores, weights))
    total_weight = sum(weights)
    
    return round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0


def identify_next_skill(user) -> Dict:
    """
    Identify skill with highest impact, lowest score.
    
    Args:
        user: User instance
        
    Returns:
        Dictionary with skill_tag and score, or None if no data
    """
    from .aggregator import get_skill_map_stats
    
    skill_map = get_skill_map_stats(user)
    skill_mastery = skill_map.get('skill_mastery', {})
    
    if not skill_mastery:
        return None
    
    # Find skill with lowest mastery score
    lowest_skill = min(skill_mastery.items(), key=lambda x: x[1]['mastery'])
    
    return {
        'skill_tag': lowest_skill[0],
        'score': lowest_skill[1]['mastery'],
        'attempts': lowest_skill[1]['attempts'],
    }


def calculate_skill_improvement(user, skill_tag: str) -> float:
    """
    Calculate improvement percentage over time for a skill.
    
    Args:
        user: User instance
        skill_tag: Skill tag string
        
    Returns:
        Improvement percentage (can be negative if declining)
    """
    completed_sessions = InterviewSession.objects.filter(
        user=user,
        status='completed'
    ).order_by('ended_at', 'started_at')
    
    skill_scores = []
    
    for session in completed_sessions:
        report = generate_report(str(session.id))
        if report and 'skill_breakdown' in report:
            skill_breakdown = report['skill_breakdown']
            if skill_tag in skill_breakdown:
                skill_scores.append(skill_breakdown[skill_tag])
    
    if len(skill_scores) < 2:
        return 0.0
    
    # Compare first half vs second half
    mid_point = len(skill_scores) // 2
    first_half_avg = sum(skill_scores[:mid_point]) / len(skill_scores[:mid_point])
    second_half_avg = sum(skill_scores[mid_point:]) / len(skill_scores[mid_point:])
    
    if first_half_avg == 0:
        return 0.0
    
    improvement = ((second_half_avg - first_half_avg) / first_half_avg) * 100
    return round(improvement, 2)


def get_top_improving_skills(user, limit: int = 5) -> List[Dict]:
    """
    Get top skills showing improvement.
    
    Args:
        user: User instance
        limit: Number of skills to return
        
    Returns:
        List of dictionaries with skill and improvement percentage
    """
    from .aggregator import get_skill_map_stats
    
    skill_map = get_skill_map_stats(user)
    skill_mastery = skill_map.get('skill_mastery', {})
    
    improvements = []
    for skill_tag in skill_mastery.keys():
        improvement = calculate_skill_improvement(user, skill_tag)
        if improvement > 0:  # Only include improving skills
            improvements.append({
                'skill': skill_tag,
                'improvement': improvement,
            })
    
    # Sort by improvement (descending) and return top N
    improvements.sort(key=lambda x: x['improvement'], reverse=True)
    return improvements[:limit]


def get_top_weak_skills(user, limit: int = 5) -> List[Dict]:
    """
    Get top skills with lowest scores.
    
    Args:
        user: User instance
        limit: Number of skills to return
        
    Returns:
        List of dictionaries with skill and score
    """
    from .aggregator import get_skill_map_stats
    
    skill_map = get_skill_map_stats(user)
    skill_mastery = skill_map.get('skill_mastery', {})
    
    weak_skills = []
    for skill_tag, data in skill_mastery.items():
        weak_skills.append({
            'skill': skill_tag,
            'score': data['mastery'],
        })
    
    # Sort by score (ascending) and return top N
    weak_skills.sort(key=lambda x: x['score'])
    return weak_skills[:limit]


def calculate_skill_trend(user, skill_tag: str) -> str:
    """
    Determine if a skill is improving, declining, or stable.
    
    Args:
        user: User instance
        skill_tag: Skill tag string
        
    Returns:
        "improving", "declining", or "stable"
    """
    improvement = calculate_skill_improvement(user, skill_tag)
    
    if improvement > 5:  # More than 5% improvement
        return "improving"
    elif improvement < -5:  # More than 5% decline
        return "declining"
    else:
        return "stable"

