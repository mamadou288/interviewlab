from typing import Dict, List
from ..models import InterviewSession, InterviewAnswer


def aggregate_scores(session: InterviewSession) -> Dict:
    """
    Calculate average scores per dimension across all answers.
    
    Args:
        session: InterviewSession instance
        
    Returns:
        Dictionary with average scores per dimension
    """
    answers = InterviewAnswer.objects.filter(question__session=session)
    
    if not answers.exists():
        return {
            'structure': 0,
            'relevance': 0,
            'technical_accuracy': 0,
            'depth': 0,
            'communication': 0,
        }
    
    totals = {
        'structure': 0,
        'relevance': 0,
        'technical_accuracy': 0,
        'depth': 0,
        'communication': 0,
    }
    
    count = 0
    for answer in answers:
        scores = answer.scores_json or {}
        for dimension in totals.keys():
            totals[dimension] += scores.get(dimension, 0)
        count += 1
    
    if count > 0:
        averages = {dim: round(totals[dim] / count, 2) for dim in totals.keys()}
    else:
        averages = totals
    
    return averages


def identify_strengths(session: InterviewSession) -> List[str]:
    """
    Extract top 3 strengths from session answers.
    
    Args:
        session: InterviewSession instance
        
    Returns:
        List of strength strings
    """
    answers = InterviewAnswer.objects.filter(question__session=session)
    
    # Collect all strengths from feedback
    all_strengths = []
    for answer in answers:
        feedback = answer.feedback_json or {}
        strengths = feedback.get('strengths', [])
        all_strengths.extend(strengths)
    
    # Count frequency of strengths
    strength_counts = {}
    for strength in all_strengths:
        strength_counts[strength] = strength_counts.get(strength, 0) + 1
    
    # Sort by frequency and return top 3
    sorted_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [strength for strength, count in sorted_strengths[:3]]


def identify_weaknesses(session: InterviewSession) -> List[str]:
    """
    Extract top 3-5 weaknesses from session answers.
    
    Args:
        session: InterviewSession instance
        
    Returns:
        List of weakness strings
    """
    answers = InterviewAnswer.objects.filter(question__session=session)
    
    # Collect all weaknesses from feedback
    all_weaknesses = []
    for answer in answers:
        feedback = answer.feedback_json or {}
        weaknesses = feedback.get('weaknesses', [])
        all_weaknesses.extend(weaknesses)
    
    # Count frequency of weaknesses
    weakness_counts = {}
    for weakness in all_weaknesses:
        weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1
    
    # Sort by frequency and return top 5
    sorted_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [weakness for weakness, count in sorted_weaknesses[:5]]


def calculate_skill_breakdown(session: InterviewSession) -> Dict:
    """
    Group scores by skill tags.
    
    Args:
        session: InterviewSession instance
        
    Returns:
        Dictionary mapping skill_tags to average scores
    """
    answers = InterviewAnswer.objects.filter(question__session=session)
    
    skill_scores = {}
    skill_counts = {}
    
    for answer in answers:
        skill_tags = answer.skill_tags_json or []
        scores = answer.scores_json or {}
        
        # Calculate average score for this answer
        if scores:
            avg_score = sum(scores.values()) / len(scores)
        else:
            avg_score = 0
        
        # Add to skill tag aggregates
        for skill_tag in skill_tags:
            if skill_tag not in skill_scores:
                skill_scores[skill_tag] = 0
                skill_counts[skill_tag] = 0
            
            skill_scores[skill_tag] += avg_score
            skill_counts[skill_tag] += 1
    
    # Calculate averages
    skill_averages = {}
    for skill_tag in skill_scores.keys():
        if skill_counts[skill_tag] > 0:
            skill_averages[skill_tag] = round(skill_scores[skill_tag] / skill_counts[skill_tag], 2)
    
    return skill_averages


def generate_report(session_id: str) -> Dict:
    """
    Main function that generates full session report.
    
    Args:
        session_id: UUID of InterviewSession
        
    Returns:
        Dictionary with complete report data
    """
    try:
        session = InterviewSession.objects.get(id=session_id)
    except InterviewSession.DoesNotExist:
        return {}
    
    # Get all answers
    answers = InterviewAnswer.objects.filter(question__session=session).select_related('question')
    
    # Aggregate scores
    rubric_breakdown = aggregate_scores(session)
    
    # Identify strengths and weaknesses
    strengths = identify_strengths(session)
    weaknesses = identify_weaknesses(session)
    
    # Calculate skill breakdown
    skill_breakdown = calculate_skill_breakdown(session)
    
    # Prepare answer summaries
    answer_summaries = []
    for answer in answers:
        answer_summaries.append({
            'question_id': str(answer.question.id),
            'question_text': answer.question.question_text,
            'answer_text': answer.answer_text,
            'scores': answer.scores_json,
            'feedback': answer.feedback_json,
            'time_seconds': answer.time_seconds,
        })
    
    return {
        'session': {
            'id': str(session.id),
            'overall_score': session.overall_score,
            'started_at': session.started_at.isoformat() if session.started_at else None,
            'ended_at': session.ended_at.isoformat() if session.ended_at else None,
        },
        'strengths': strengths,
        'weaknesses': weaknesses,
        'rubric_breakdown': rubric_breakdown,
        'skill_breakdown': skill_breakdown,
        'answers': answer_summaries,
    }

