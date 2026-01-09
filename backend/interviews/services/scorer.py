import re
from typing import Dict


def score_structure(answer_text: str, question) -> int:
    """
    Score structure dimension (0-5).
    
    Checks for:
    - STAR format keywords
    - Logical flow indicators
    - Answer length appropriateness
    """
    score = 0
    answer_lower = answer_text.lower()
    word_count = len(answer_text.split())
    
    # Check for STAR keywords
    star_keywords = ['situation', 'task', 'action', 'result', 'outcome', 'challenge', 'problem']
    star_found = sum(1 for keyword in star_keywords if keyword in answer_lower)
    if star_found >= 3:
        score += 3
    elif star_found >= 2:
        score += 2
    elif star_found >= 1:
        score += 1
    
    # Check for logical flow indicators
    flow_indicators = ['first', 'then', 'next', 'finally', 'because', 'therefore', 'however']
    flow_count = sum(1 for indicator in flow_indicators if indicator in answer_lower)
    if flow_count >= 3:
        score += 1
    elif flow_count >= 1:
        score += 0.5
    
    # Check answer length (appropriate length indicates structure)
    if 50 <= word_count <= 300:
        score += 1
    elif word_count < 30:
        score -= 1  # Too short
    
    # Normalize to 0-5
    score = max(0, min(5, int(score)))
    return score


def score_relevance(answer_text: str, question) -> int:
    """
    Score relevance dimension (0-5).
    
    Checks if answer addresses the question.
    """
    score = 3  # Start with neutral score
    answer_lower = answer_text.lower()
    question_lower = question.question_text.lower()
    
    # Extract key terms from question
    question_words = set(re.findall(r'\b\w+\b', question_lower))
    answer_words = set(re.findall(r'\b\w+\b', answer_lower))
    
    # Check for question keywords in answer
    common_words = question_words.intersection(answer_words)
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    common_words = common_words - stop_words
    
    if len(common_words) >= 3:
        score += 2
    elif len(common_words) >= 1:
        score += 1
    
    # Check answer length (too short might be off-topic)
    word_count = len(answer_text.split())
    if word_count < 20:
        score -= 2
    elif word_count < 30:
        score -= 1
    
    # Normalize to 0-5
    score = max(0, min(5, int(score)))
    return score


def score_technical_accuracy(answer_text: str, question) -> int:
    """
    Score technical accuracy dimension (0-5).
    
    Checks for correct technical terms and concepts.
    """
    if question.category != 'technical':
        return 3  # Neutral for non-technical questions
    
    score = 2  # Start with low score
    answer_lower = answer_text.lower()
    
    # Check for technical terms based on skill tags
    skill_tags = question.skill_tags_json or []
    
    # Map skill tags to expected keywords
    expected_keywords = {
        'backend.api.rest': ['rest', 'http', 'endpoint', 'request', 'response'],
        'backend.database': ['database', 'sql', 'query', 'table', 'index'],
        'backend.auth': ['authentication', 'authorization', 'token', 'session', 'jwt'],
        'frontend.react': ['react', 'component', 'props', 'state', 'hook'],
        'frontend.javascript': ['javascript', 'function', 'variable', 'closure', 'promise'],
    }
    
    # Check for expected keywords
    found_keywords = 0
    for tag in skill_tags:
        keywords = expected_keywords.get(tag, [])
        for keyword in keywords:
            if keyword in answer_lower:
                found_keywords += 1
    
    if found_keywords >= 5:
        score = 5
    elif found_keywords >= 3:
        score = 4
    elif found_keywords >= 1:
        score = 3
    
    # Check for common technical errors (negative indicators)
    error_indicators = ['i think', 'maybe', 'not sure', 'i guess']
    error_count = sum(1 for indicator in error_indicators if indicator in answer_lower)
    if error_count >= 2:
        score -= 1
    
    # Normalize to 0-5
    score = max(0, min(5, int(score)))
    return score


def score_depth(answer_text: str, question) -> int:
    """
    Score depth dimension (0-5).
    
    Checks for detail level, examples, and tradeoffs.
    """
    score = 2  # Start with low score
    answer_lower = answer_text.lower()
    word_count = len(answer_text.split())
    
    # Check answer length (longer answers tend to be more detailed)
    if word_count >= 200:
        score += 2
    elif word_count >= 100:
        score += 1
    elif word_count < 50:
        score -= 1
    
    # Check for examples
    example_indicators = ['for example', 'for instance', 'such as', 'like', 'example']
    if any(indicator in answer_lower for indicator in example_indicators):
        score += 1
    
    # Check for tradeoffs/considerations
    tradeoff_indicators = ['however', 'but', 'tradeoff', 'consideration', 'pros and cons', 'advantage', 'disadvantage']
    if any(indicator in answer_lower for indicator in tradeoff_indicators):
        score += 1
    
    # Check for explanations (why/how)
    explanation_indicators = ['because', 'why', 'how', 'reason', 'due to']
    if any(indicator in answer_lower for indicator in explanation_indicators):
        score += 0.5
    
    # Normalize to 0-5
    score = max(0, min(5, int(score)))
    return score


def score_communication(answer_text: str, question) -> int:
    """
    Score communication dimension (0-5).
    
    Checks for clarity, structure, and readability.
    """
    score = 3  # Start with neutral score
    word_count = len(answer_text.split())
    
    # Check for proper sentence structure (periods indicate sentences)
    sentence_count = answer_text.count('.') + answer_text.count('!') + answer_text.count('?')
    if sentence_count >= 3:
        score += 1
    elif sentence_count < 1:
        score -= 1
    
    # Check answer length (appropriate length indicates good communication)
    if 50 <= word_count <= 300:
        score += 1
    elif word_count < 30:
        score -= 1  # Too short, unclear
    elif word_count > 500:
        score -= 0.5  # Too verbose
    
    # Check for transitions (indicates good flow)
    transitions = ['first', 'second', 'then', 'next', 'finally', 'additionally', 'furthermore', 'moreover']
    transition_count = sum(1 for trans in transitions if trans in answer_text.lower())
    if transition_count >= 2:
        score += 1
    
    # Check for clarity indicators
    clarity_indicators = ['clearly', 'specifically', 'in other words', 'to clarify']
    if any(indicator in answer_text.lower() for indicator in clarity_indicators):
        score += 0.5
    
    # Normalize to 0-5
    score = max(0, min(5, int(score)))
    return score


def score_answer(answer_text: str, question) -> Dict:
    """
    Main scoring function that scores all dimensions.
    
    Args:
        answer_text: User's answer text
        question: InterviewQuestion instance
        
    Returns:
        Dictionary with all dimension scores
    """
    scores = {
        'structure': score_structure(answer_text, question),
        'relevance': score_relevance(answer_text, question),
        'technical_accuracy': score_technical_accuracy(answer_text, question),
        'depth': score_depth(answer_text, question),
        'communication': score_communication(answer_text, question),
    }
    
    return scores


def calculate_overall_score(scores: Dict) -> int:
    """
    Calculate overall score from rubric scores (0-100 scale).
    
    Args:
        scores: Dictionary with dimension scores (0-5 each)
        
    Returns:
        Overall score (0-100)
    """
    overall = (
        scores.get('structure', 0) * 0.2 +
        scores.get('relevance', 0) * 0.2 +
        scores.get('technical_accuracy', 0) * 0.25 +
        scores.get('depth', 0) * 0.2 +
        scores.get('communication', 0) * 0.15
    ) * 20
    
    return int(round(overall))

