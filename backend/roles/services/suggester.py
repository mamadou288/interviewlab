from typing import Dict, List
from decimal import Decimal
from profiles.models import CVDocument, Profile
from ..models import RoleCatalog, RoleSuggestion


def extract_profile_keywords(profile_data: Dict) -> List[str]:
    """
    Extract keywords from profile data_json.
    
    Args:
        profile_data: Profile data_json dictionary
        
    Returns:
        List of normalized keywords (lowercase)
    """
    keywords = []
    
    # Extract skills
    skills = profile_data.get('skills', [])
    for skill in skills:
        if isinstance(skill, str):
            # Normalize skill (lowercase, strip)
            normalized = skill.lower().strip()
            if normalized:
                keywords.append(normalized)
    
    # Extract job titles from experience
    experience = profile_data.get('experience', [])
    for exp in experience:
        if isinstance(exp, dict):
            title = exp.get('title', '')
            if title:
                # Extract words from title
                words = title.lower().split()
                keywords.extend(words)
    
    # Extract technologies from projects
    projects = profile_data.get('projects', [])
    for project in projects:
        if isinstance(project, dict):
            # Extract from project name and description
            name = project.get('name', '')
            description = project.get('description', '')
            if name:
                words = name.lower().split()
                keywords.extend(words)
            if description:
                words = description.lower().split()
                keywords.extend(words)
    
    # Remove duplicates and return
    return list(set(keywords))


def calculate_role_score(profile_keywords: List[str], role: RoleCatalog) -> float:
    """
    Calculate similarity score between profile and role.
    
    Args:
        profile_keywords: List of normalized profile keywords
        role: RoleCatalog instance
        
    Returns:
        Score from 0.0 to 1.0
    """
    score = 0.0
    
    # Normalize role keywords
    role_keywords = [kw.lower().strip() for kw in role.keywords_json if isinstance(kw, str)]
    role_name_words = role.name.lower().split()
    
    # Title match (0.3 max)
    # Check if role name or key words appear in profile keywords
    role_name_lower = role.name.lower()
    for keyword in profile_keywords:
        if role_name_lower in keyword or keyword in role_name_lower:
            score += 0.3
            break
    
    # Also check if any role name word matches experience titles
    for role_word in role_name_words:
        if role_word in profile_keywords:
            score += 0.3
            break
    
    # Skill matches (0.5 max)
    matched_skills = 0
    for profile_keyword in profile_keywords:
        if profile_keyword in role_keywords:
            matched_skills += 1
    
    skill_score = min(matched_skills * 0.1, 0.5)
    score += skill_score
    
    # Keyword matches (0.2 max)
    # Count additional keyword matches beyond skills
    matched_keywords = 0
    for role_keyword in role_keywords:
        if role_keyword in profile_keywords:
            matched_keywords += 1
    
    keyword_score = min(matched_keywords * 0.05, 0.2)
    score += keyword_score
    
    # Normalize to 0.0-1.0
    score = min(score, 1.0)
    
    return round(score, 2)


def generate_reasons(profile_data: Dict, role: RoleCatalog, score: float) -> List[str]:
    """
    Generate human-readable reasons for suggestion.
    
    Args:
        profile_data: Profile data_json dictionary
        role: RoleCatalog instance
        score: Calculated score
        
    Returns:
        List of reason strings
    """
    reasons = []
    
    # Extract profile keywords
    profile_keywords = extract_profile_keywords(profile_data)
    role_keywords = [kw.lower().strip() for kw in role.keywords_json if isinstance(kw, str)]
    
    # Count matched skills
    matched_skills = []
    profile_skills = [s.lower().strip() for s in profile_data.get('skills', []) if isinstance(s, str)]
    
    for skill in profile_skills:
        if skill in role_keywords:
            matched_skills.append(skill)
    
    if matched_skills:
        reasons.append(f"Matched {len(matched_skills)} skills: {', '.join(matched_skills[:5])}")
    
    # Check experience relevance
    experience = profile_data.get('experience', [])
    if experience:
        reasons.append(f"Relevant experience: {len(experience)} position(s)")
    
    # Check if role name matches experience titles
    role_name_lower = role.name.lower()
    for exp in experience:
        if isinstance(exp, dict):
            title = exp.get('title', '').lower()
            if role_name_lower in title or any(word in title for word in role_name_lower.split()):
                reasons.append(f"Experience matches role: {exp.get('title', '')}")
                break
    
    # If no specific reasons, add generic one
    if not reasons:
        reasons.append(f"Partial match based on profile keywords")
    
    return reasons[:3]  # Return max 3 reasons


def suggest_roles(cv_document_id: str) -> List[RoleSuggestion]:
    """
    Main function that generates role suggestions for a CV document.
    
    Args:
        cv_document_id: UUID of CVDocument
        
    Returns:
        List of RoleSuggestion objects (top 10, sorted by score)
    """
    # Get CVDocument
    try:
        cv_document = CVDocument.objects.get(id=cv_document_id)
    except CVDocument.DoesNotExist:
        return []
    
    # Get associated Profile
    try:
        profile = Profile.objects.get(user=cv_document.user)
        profile_data = profile.data_json
    except Profile.DoesNotExist:
        # If no profile, return empty suggestions
        return []
    
    # Extract profile keywords
    profile_keywords = extract_profile_keywords(profile_data)
    
    # Get all roles from catalog
    roles = RoleCatalog.objects.all()
    
    # Calculate scores and create suggestions
    suggestions_data = []
    
    for role in roles:
        score = calculate_role_score(profile_keywords, role)
        reasons = generate_reasons(profile_data, role, score)
        
        # Only include roles with score > 0
        if score > 0:
            suggestions_data.append({
                'role': role,
                'score': score,
                'reasons': reasons
            })
    
    # Sort by score (descending)
    suggestions_data.sort(key=lambda x: x['score'], reverse=True)
    
    # Create/update RoleSuggestion records for top 10
    top_suggestions = suggestions_data[:10]
    role_suggestions = []
    
    for suggestion_data in top_suggestions:
        role_suggestion, created = RoleSuggestion.objects.update_or_create(
            cv_document=cv_document,
            role=suggestion_data['role'],
            defaults={
                'score': Decimal(str(suggestion_data['score'])),
                'reasons_json': suggestion_data['reasons']
            }
        )
        role_suggestions.append(role_suggestion)
    
    return role_suggestions

