from typing import List, Dict, Set
from interviews.models import InterviewSession, InterviewAnswer
from interviews.services.report import generate_report
from profiles.models import Profile
from roles.models import RoleCatalog
from ..models import PlanTemplate, UpgradePlan
from .template_generator import generate_template_for_skill


def get_user_profile_skills(user) -> Set[str]:
    """
    Extract skills from user's profile.
    
    Args:
        user: User instance
        
    Returns:
        Set of skill keywords (normalized)
    """
    try:
        profile = Profile.objects.get(user=user)
        profile_data = profile.data_json or {}
    except Profile.DoesNotExist:
        return set()
    
    skills = set()
    
    # Extract from skills list
    profile_skills = profile_data.get('skills', [])
    for skill in profile_skills:
        if isinstance(skill, str):
            skills.add(skill.lower().strip())
    
    # Extract from experience job titles
    experience = profile_data.get('experience', [])
    for exp in experience:
        if isinstance(exp, dict):
            title = exp.get('title', '')
            if title:
                words = title.lower().split()
                skills.update(words)
    
    # Extract from projects technologies
    projects = profile_data.get('projects', [])
    for project in projects:
        if isinstance(project, dict):
            technologies = project.get('technologies', [])
            for tech in technologies:
                if isinstance(tech, str):
                    skills.add(tech.lower().strip())
    
    return skills


def get_interview_history_skills(user) -> Dict[str, float]:
    """
    Get skill tags from all user's completed interview sessions with average scores.
    
    Args:
        user: User instance
        
    Returns:
        Dictionary mapping skill_tags to average scores across all interviews
    """
    completed_sessions = InterviewSession.objects.filter(
        user=user,
        status='completed'
    )
    
    skill_scores = {}
    skill_counts = {}
    
    for session in completed_sessions:
        answers = InterviewAnswer.objects.filter(question__session=session)
        
        for answer in answers:
            skill_tags = answer.skill_tags_json or []
            scores = answer.scores_json or {}
            
            # Calculate average score for this answer
            if scores:
                avg_score = sum(scores.values()) / len(scores)
            else:
                avg_score = 0
            
            # Aggregate by skill tag
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
            skill_averages[skill_tag] = skill_scores[skill_tag] / skill_counts[skill_tag]
    
    return skill_averages


def identify_skill_gaps(user, role: RoleCatalog, current_session: InterviewSession) -> List[str]:
    """
    Identify skill gaps by comparing:
    - Role requirements (from role keywords)
    - User profile skills
    - Interview history performance
    - Current interview weak skills
    
    Args:
        user: User instance
        role: RoleCatalog instance
        current_session: Current InterviewSession
        
    Returns:
        List of skill tags that need improvement (prioritized)
    """
    gaps = []
    
    # Get role keywords (what skills are needed for this role)
    role_keywords = [kw.lower().strip() for kw in role.keywords_json if isinstance(kw, str)]
    
    # Get user profile skills
    profile_skills = get_user_profile_skills(user)
    
    # Get interview history skills with scores
    history_skills = get_interview_history_skills(user)
    
    # Get current session weak skills
    report = generate_report(str(current_session.id))
    current_skill_breakdown = report.get('skill_breakdown', {}) if report else {}
    
    # Identify gaps:
    # 1. Skills needed for role but weak in current interview
    for skill_tag, score in current_skill_breakdown.items():
        if score < 3.0:  # Weak skill
            gaps.append((skill_tag, score, 'current_weak'))
    
    # 2. Skills needed for role but consistently weak in history
    for skill_tag, avg_score in history_skills.items():
        if avg_score < 3.0 and skill_tag not in [g[0] for g in gaps]:
            # Check if this skill is relevant to the role
            skill_parts = skill_tag.split('.')
            if any(part in role_keywords for part in skill_parts):
                gaps.append((skill_tag, avg_score, 'history_weak'))
    
    # 3. Role keywords that don't appear in profile or interviews
    for keyword in role_keywords:
        # Check if keyword matches any skill tag pattern
        matching_skills = [
            tag for tag, score, source in gaps
            if keyword in tag or any(part == keyword for part in tag.split('.'))
        ]
        
        if not matching_skills:
            # Check if keyword appears in profile
            if keyword not in profile_skills:
                # Try to find a template that matches this keyword
                try:
                    template = PlanTemplate.objects.filter(
                        skill_tag__icontains=keyword
                    ).first()
                    if template and template.skill_tag not in [g[0] for g in gaps]:
                        gaps.append((template.skill_tag, 0.0, 'missing'))
                except:
                    pass
    
    # Sort by priority: current_weak > history_weak > missing, then by score (lowest first)
    priority_order = {'current_weak': 1, 'history_weak': 2, 'missing': 3}
    gaps.sort(key=lambda x: (priority_order.get(x[2], 99), x[1]))
    
    # Return top 5 skill tags
    return [skill_tag for skill_tag, score, source in gaps[:5]]


def identify_weak_skills(session: InterviewSession) -> List[str]:
    """
    Extract weak skill tags from interview report.
    
    Args:
        session: InterviewSession instance
        
    Returns:
        List of skill tags with score < 3.0 (top 5, sorted by score ascending)
    """
    report = generate_report(str(session.id))
    
    if not report:
        return []
    
    skill_breakdown = report.get('skill_breakdown', {})
    
    # Filter skills with score < 3.0 (weak skills)
    weak_skills = [
        (skill_tag, score)
        for skill_tag, score in skill_breakdown.items()
        if score < 3.0
    ]
    
    # Sort by score (lowest first)
    weak_skills.sort(key=lambda x: x[1])
    
    # Return top 5 skill tags
    return [skill_tag for skill_tag, score in weak_skills[:5]]


def select_templates(weak_skills: List[str], user=None, role: RoleCatalog = None, user_level: str = 'mid') -> List[PlanTemplate]:
    """
    Generate or retrieve plan templates dynamically based on skills, user profile, and level.
    
    Args:
        weak_skills: List of skill tags from current interview
        user: User instance (optional, for profile-based selection)
        role: RoleCatalog instance (optional, for role-based selection)
        user_level: User level ('junior', 'mid', 'senior')
        
    Returns:
        List of PlanTemplate objects (top 3-5)
    """
    templates = []
    matched_tags = set()
    role_keywords = []
    
    if role:
        role_keywords = [kw.lower().strip() for kw in role.keywords_json if isinstance(kw, str)]
    
    # Generate templates dynamically for each skill
    for skill_tag in weak_skills:
        if skill_tag in matched_tags:
            continue
        
        try:
            # Try to get existing template first
            template = PlanTemplate.objects.get(skill_tag=skill_tag)
            templates.append(template)
            matched_tags.add(skill_tag)
        except PlanTemplate.DoesNotExist:
            # Generate template dynamically based on user level
            try:
                template = generate_template_for_skill(skill_tag, user_level, role_keywords)
                templates.append(template)
                matched_tags.add(skill_tag)
            except Exception:
                # Skip if generation fails
                continue
    
    # If not enough templates, try partial matches and generate
    if len(templates) < 3:
        for skill_tag in weak_skills:
            if skill_tag in matched_tags:
                continue
            
            # Try partial match (e.g., "backend.django" matches "backend.django.auth")
            parts = skill_tag.split('.')
            for i in range(len(parts), 0, -1):
                partial_tag = '.'.join(parts[:i])
                try:
                    template = PlanTemplate.objects.get(skill_tag=partial_tag)
                    if template not in templates:
                        templates.append(template)
                        matched_tags.add(skill_tag)
                        break
                except PlanTemplate.DoesNotExist:
                    # Generate template for partial tag
                    try:
                        template = generate_template_for_skill(partial_tag, user_level, role_keywords)
                        if template not in templates:
                            templates.append(template)
                            matched_tags.add(skill_tag)
                            break
                    except Exception:
                        continue
    
    # If user and role provided, enhance selection with profile and history
    if user and role:
        # Get skill gaps considering profile and history
        try:
            # We need current_session, but we can use weak_skills as proxy
            # For now, prioritize templates that match role requirements
            role_keywords = [kw.lower().strip() for kw in role.keywords_json if isinstance(kw, str)]
            profile_skills = get_user_profile_skills(user)
            
            # Score templates based on relevance
            template_scores = []
            for template in templates:
                score = 0
                skill_parts = template.skill_tag.split('.')
                
                # Higher score if matches role keywords
                if any(kw in template.skill_tag for kw in role_keywords):
                    score += 2
                
                # Higher score if user doesn't have this skill in profile
                if not any(part in profile_skills for part in skill_parts):
                    score += 1
                
                template_scores.append((template, score))
            
            # Sort by score (highest first)
            template_scores.sort(key=lambda x: x[1], reverse=True)
            templates = [t for t, s in template_scores]
        except Exception:
            pass  # Fall back to original logic
    
    # Ensure variety (not all same difficulty)
    if templates:
        # Group by difficulty
        by_difficulty = {'beginner': [], 'intermediate': [], 'advanced': []}
        for template in templates:
            by_difficulty[template.difficulty].append(template)
        
        # Try to have at least one from each difficulty if possible
        result = []
        if by_difficulty['beginner']:
            result.append(by_difficulty['beginner'][0])
        if by_difficulty['intermediate']:
            result.append(by_difficulty['intermediate'][0])
        if by_difficulty['advanced']:
            result.append(by_difficulty['advanced'][0])
        
        # Add remaining templates
        for template in templates:
            if template not in result:
                result.append(template)
        
        templates = result
    
    return templates[:5]


def compose_daily_plan(templates: List[PlanTemplate], duration_days: int) -> List[Dict]:
    """
    Distribute templates across days.
    
    Args:
        templates: List of PlanTemplate objects
        duration_days: 7 or 14
        
    Returns:
        List of daily plan dictionaries
    """
    daily_plans = []
    
    if not templates:
        return daily_plans
    
    # Calculate how many templates to use
    if duration_days == 7:
        templates_to_use = templates[:2]  # Use 1-2 templates
    else:  # 14 days
        templates_to_use = templates[:3]  # Use 2-3 templates
    
    # Collect all steps from templates
    all_steps = []
    for template in templates_to_use:
        steps = template.steps_json or []
        for step in steps:
            step['template_skill'] = template.skill_tag
            step['template_title'] = template.title
        all_steps.extend(steps)
    
    # Distribute steps across days
    steps_per_day = max(1, len(all_steps) // duration_days)
    
    current_day = 1
    current_steps = []
    
    for step in all_steps:
        current_steps.append(step)
        
        # If we have enough steps for a day, or it's the last step
        if len(current_steps) >= steps_per_day or step == all_steps[-1]:
            # Combine steps for this day
            daily_plan = {
                'day': current_day,
                'topic': current_steps[0].get('topic', ''),
                'drills': [],
                'mini_mock': current_steps[0].get('mini_mock', ''),
                'quick_test': current_steps[0].get('quick_test', ''),
            }
            
            # Collect all drills from steps
            for s in current_steps:
                daily_plan['drills'].extend(s.get('drills', []))
            
            daily_plans.append(daily_plan)
            current_day += 1
            current_steps = []
            
            if current_day > duration_days:
                break
    
    # Fill remaining days if needed
    while len(daily_plans) < duration_days:
        daily_plans.append({
            'day': len(daily_plans) + 1,
            'topic': 'Review and Practice',
            'drills': ['Review previous days\' material', 'Practice with mock questions'],
            'mini_mock': 'Practice question from previous days',
            'quick_test': 'Complete quick test from earlier topics'
        })
    
    return daily_plans[:duration_days]


def generate_learning_objectives(weaknesses: List[str], skill_breakdown: Dict) -> List[str]:
    """
    Convert weaknesses to specific, measurable learning objectives.
    
    Args:
        weaknesses: List of weakness strings from report
        skill_breakdown: Dictionary mapping skill tags to scores
        
    Returns:
        List of 3-5 learning objectives
    """
    objectives = []
    
    # Map common weaknesses to objectives
    weakness_to_objective = {
        'star': 'Use STAR method (Situation, Task, Action, Result) in every behavioral answer',
        'structure': 'Structure all answers with clear organization and logical flow',
        'django auth': 'Explain Django authentication flow including sessions, tokens, and security',
        'sql joins': 'Solve 10 SQL join exercises and explain reasoning clearly',
        'depth': 'Provide detailed explanations with examples and tradeoffs',
        'technical': 'Review technical concepts and ensure accuracy in explanations',
        'communication': 'Focus on clarity and conciseness in communication',
    }
    
    # Extract objectives from weaknesses
    weaknesses_lower = [w.lower() for w in weaknesses]
    
    for key, objective in weakness_to_objective.items():
        if any(key in w for w in weaknesses_lower):
            objectives.append(objective)
    
    # Generate objectives from skill breakdown
    weak_skills = [tag for tag, score in skill_breakdown.items() if score < 3.0]
    
    for skill_tag in weak_skills[:3]:
        if 'communication.star' in skill_tag:
            objectives.append('Master STAR method for behavioral questions')
        elif 'backend.django.auth' in skill_tag:
            objectives.append('Explain JWT flow and refresh tokens clearly')
        elif 'sql.joins' in skill_tag:
            objectives.append('Master SQL joins and explain join logic')
        elif 'system_design' in skill_tag:
            objectives.append('Design scalable systems with proper architecture')
    
    # Ensure we have at least 3 objectives
    if len(objectives) < 3:
        objectives.append('Improve answer structure and organization')
        objectives.append('Add more details and examples to answers')
        objectives.append('Practice explaining concepts clearly')
    
    return objectives[:5]


def recommend_next_interview(session: InterviewSession, weaknesses: List[str]) -> Dict:
    """
    Generate next interview recommendation based on weaknesses.
    
    Args:
        session: InterviewSession instance
        weaknesses: List of weakness strings
        
    Returns:
        Dictionary with type, difficulty, focus_topics, timer
    """
    weaknesses_lower = [w.lower() for w in weaknesses]
    
    # Determine interview type based on weaknesses
    interview_type = 'mixed'
    focus_topics = []
    
    # Check for behavioral/communication weaknesses
    if any('star' in w or 'behavioral' in w or 'structure' in w for w in weaknesses_lower):
        interview_type = 'hr'
        focus_topics.append('STAR Method')
        focus_topics.append('Behavioral Questions')
    
    # Check for technical weaknesses
    if any('technical' in w or 'django' in w or 'sql' in w or 'algorithm' in w for w in weaknesses_lower):
        if interview_type == 'hr':
            interview_type = 'mixed'
        else:
            interview_type = 'technical'
        focus_topics.append('Technical Concepts')
    
    # Check for system design weaknesses
    if any('system design' in w or 'scaling' in w or 'architecture' in w for w in weaknesses_lower):
        if interview_type == 'hr':
            interview_type = 'mixed'
        else:
            interview_type = 'case'
        focus_topics.append('System Design')
    
    # Set difficulty based on current session level
    difficulty = session.level  # Use same level
    
    # Recommend timer based on type
    timer = 90 if interview_type == 'hr' else 120
    
    # Extract specific focus topics from weaknesses
    if 'star' in ' '.join(weaknesses_lower):
        focus_topics.append('STAR Format')
    if 'django' in ' '.join(weaknesses_lower):
        focus_topics.append('Django Authentication')
    if 'sql' in ' '.join(weaknesses_lower):
        focus_topics.append('SQL Joins')
    
    return {
        'type': interview_type,
        'difficulty': difficulty,
        'focus_topics': focus_topics[:4],  # Max 4 topics
        'timer': timer
    }


def generate_upgrade_plan(session_id: str, duration_days: int = 7) -> UpgradePlan:
    """
    Main function that generates upgrade plan for a session.
    
    Args:
        session_id: UUID of InterviewSession
        duration_days: 7 or 14 (default: 7)
        
    Returns:
        UpgradePlan instance
    """
    # Get session
    try:
        session = InterviewSession.objects.get(id=session_id)
    except InterviewSession.DoesNotExist:
        raise ValueError(f"Interview session {session_id} not found")
    
    # Check if session is completed
    if session.status != 'completed':
        raise ValueError("Interview session must be completed to generate upgrade plan")
    
    # Generate report
    report = generate_report(session_id)
    
    if not report:
        raise ValueError("Could not generate interview report")
    
    # Get strengths and weaknesses
    strengths = report.get('strengths', [])
    weaknesses = report.get('weaknesses', [])
    skill_breakdown = report.get('skill_breakdown', {})
    
    # Identify weak skills from current interview
    weak_skills = identify_weak_skills(session)
    
    # Identify skill gaps considering profile and interview history
    skill_gaps = identify_skill_gaps(session.user, session.role_selected, session)
    
    # Combine weak skills and gaps, prioritizing gaps
    # skill_gaps is already a list of skill tags (strings)
    all_skills = skill_gaps + weak_skills
    # Remove duplicates while preserving order
    unique_skills = []
    seen = set()
    for skill in all_skills:
        if skill not in seen:
            unique_skills.append(skill)
            seen.add(skill)
    
    # Select templates considering user profile, role, and level
    templates = select_templates(
        unique_skills,
        user=session.user,
        role=session.role_selected,
        user_level=session.level
    )
    
    # Compose daily plan
    daily_plans = compose_daily_plan(templates, duration_days)
    
    # Generate learning objectives
    learning_objectives = generate_learning_objectives(weaknesses, skill_breakdown)
    
    # Recommend next interview
    next_interview = recommend_next_interview(session, weaknesses)
    
    # Create plan_json
    plan_json = {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'learning_objectives': learning_objectives,
        'daily_plans': daily_plans,
        'next_interview': next_interview,
    }
    
    # Create or update UpgradePlan
    upgrade_plan, created = UpgradePlan.objects.update_or_create(
        session=session,
        duration_days=duration_days,
        defaults={'plan_json': plan_json}
    )
    
    return upgrade_plan

