from typing import Dict, List


def generate_strengths(scores: Dict, answer_text: str, question) -> List[str]:
    """
    Generate 3 strengths based on scores and answer.
    
    Args:
        scores: Dictionary with dimension scores
        answer_text: User's answer
        question: InterviewQuestion instance
        
    Returns:
        List of strength strings
    """
    strengths = []
    
    # Find highest scoring dimensions
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    for dimension, score in sorted_scores[:3]:
        if score >= 4:
            if dimension == 'structure':
                strengths.append("Well-structured answer with clear organization")
            elif dimension == 'relevance':
                strengths.append("Answer directly addresses the question")
            elif dimension == 'technical_accuracy':
                strengths.append("Technically accurate with correct terminology")
            elif dimension == 'depth':
                strengths.append("Detailed answer with good examples")
            elif dimension == 'communication':
                strengths.append("Clear and concise communication")
    
    # If not enough strengths, add generic ones
    if len(strengths) < 3:
        if scores.get('structure', 0) >= 3:
            strengths.append("Good structure and organization")
        if scores.get('relevance', 0) >= 3:
            strengths.append("Relevant to the question asked")
        if scores.get('communication', 0) >= 3:
            strengths.append("Clear communication style")
    
    return strengths[:3]


def generate_weaknesses(scores: Dict, answer_text: str, question) -> List[str]:
    """
    Generate 3-5 weaknesses based on scores and answer.
    
    Args:
        scores: Dictionary with dimension scores
        answer_text: User's answer
        question: InterviewQuestion instance
        
    Returns:
        List of weakness strings
    """
    weaknesses = []
    
    # Find lowest scoring dimensions
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
    
    for dimension, score in sorted_scores:
        if score < 3:
            if dimension == 'structure':
                if 'situation' not in answer_text.lower() and question.category == 'behavioral':
                    weaknesses.append("Answers lack structure (no STAR format)")
                else:
                    weaknesses.append("Answer structure could be improved")
            elif dimension == 'relevance':
                weaknesses.append("Answer could be more directly relevant to the question")
            elif dimension == 'technical_accuracy':
                weaknesses.append("Technical accuracy needs improvement - verify technical concepts")
            elif dimension == 'depth':
                weaknesses.append("Answer is too shallow - add more details and examples")
            elif dimension == 'communication':
                weaknesses.append("Communication clarity could be improved")
    
    # Add specific feedback based on question type
    if question.category == 'behavioral' and scores.get('structure', 0) < 3:
        weaknesses.append("Use STAR method (Situation, Task, Action, Result) for behavioral questions")
    
    if question.category == 'technical' and scores.get('depth', 0) < 3:
        weaknesses.append("Provide more technical depth and explain concepts in detail")
    
    # Ensure we have at least 2 weaknesses
    if len(weaknesses) < 2:
        weaknesses.append("Consider expanding your answer with more examples and details")
    
    return weaknesses[:5]


def generate_model_answer(question) -> str:
    """
    Generate a basic model answer structure (optional).
    
    Args:
        question: InterviewQuestion instance
        
    Returns:
        Model answer string
    """
    # Basic template - can be enhanced with LLM later
    if question.category == 'behavioral':
        return "A good answer would follow the STAR method: Situation (context), Task (what needed to be done), Action (what you did), Result (outcome)."
    elif question.category == 'technical':
        return "A good technical answer would explain the concept clearly, provide examples, and discuss tradeoffs or considerations."
    else:
        return "A good answer would be clear, relevant, detailed, and well-structured."


def generate_improvements(weaknesses: List[str]) -> List[str]:
    """
    Generate improvement suggestions from weaknesses.
    
    Args:
        weaknesses: List of weakness strings
        
    Returns:
        List of improvement suggestions
    """
    improvements = []
    
    for weakness in weaknesses:
        if 'STAR' in weakness:
            improvements.append("Practice using STAR method: Structure answers as Situation, Task, Action, Result")
        elif 'depth' in weakness.lower() or 'shallow' in weakness.lower():
            improvements.append("Add more details, examples, and explanations to your answers")
        elif 'structure' in weakness.lower():
            improvements.append("Organize your answer with clear sections and logical flow")
        elif 'technical' in weakness.lower():
            improvements.append("Review technical concepts and ensure accuracy in your explanations")
        elif 'communication' in weakness.lower():
            improvements.append("Focus on clarity and conciseness in your communication")
    
    # Add generic improvements if needed
    if len(improvements) < 3:
        improvements.append("Practice answering questions out loud to improve clarity")
        improvements.append("Review your answers for completeness and relevance")
    
    return improvements[:5]


def generate_feedback(answer_text: str, scores: Dict, question) -> Dict:
    """
    Main function that generates complete feedback.
    
    Args:
        answer_text: User's answer
        scores: Dictionary with dimension scores
        question: InterviewQuestion instance
        
    Returns:
        Dictionary with strengths, weaknesses, model_answer, improvements
    """
    strengths = generate_strengths(scores, answer_text, question)
    weaknesses = generate_weaknesses(scores, answer_text, question)
    model_answer = generate_model_answer(question)
    improvements = generate_improvements(weaknesses)
    
    return {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'model_answer': model_answer,
        'improvements': improvements,
    }

