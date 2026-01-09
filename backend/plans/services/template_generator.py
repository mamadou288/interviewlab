from typing import Dict, List
from ..models import PlanTemplate


def generate_template_for_skill(skill_tag: str, user_level: str, role_keywords: List[str] = None) -> PlanTemplate:
    """
    Generate a plan template dynamically for a specific skill tag and user level.
    
    Args:
        skill_tag: Skill tag (e.g., "communication.star", "backend.django.auth")
        user_level: 'junior', 'mid', or 'senior'
        role_keywords: Optional list of role keywords for context
        
    Returns:
        PlanTemplate instance
    """
    # Check if template already exists
    try:
        existing = PlanTemplate.objects.get(skill_tag=skill_tag)
        return existing
    except PlanTemplate.DoesNotExist:
        pass
    
    # Generate template based on skill tag and level
    template_data = _generate_template_content(skill_tag, user_level, role_keywords or [])
    
    # Create template
    template = PlanTemplate.objects.create(
        skill_tag=skill_tag,
        title=template_data['title'],
        description=template_data['description'],
        steps_json=template_data['steps_json'],
        difficulty=template_data['difficulty'],
        duration_minutes=template_data['duration_minutes']
    )
    
    return template


def _generate_template_content(skill_tag: str, level: str, role_keywords: List[str]) -> Dict:
    """
    Generate template content based on skill tag and level.
    
    Args:
        skill_tag: Skill tag
        level: User level
        role_keywords: Role keywords for context
        
    Returns:
        Dictionary with template data
    """
    # Determine difficulty based on level
    difficulty_map = {
        'junior': 'beginner',
        'mid': 'intermediate',
        'senior': 'advanced'
    }
    difficulty = difficulty_map.get(level, 'intermediate')
    
    # Determine number of days based on level
    days_map = {
        'junior': 3,
        'mid': 5,
        'senior': 7
    }
    num_days = days_map.get(level, 5)
    
    # Generate content based on skill tag category
    if 'communication.star' in skill_tag or 'behavioral' in skill_tag:
        return _generate_star_template(level, num_days, difficulty)
    elif 'backend' in skill_tag or 'django' in skill_tag:
        return _generate_backend_template(skill_tag, level, num_days, difficulty)
    elif 'sql' in skill_tag or 'database' in skill_tag:
        return _generate_sql_template(level, num_days, difficulty)
    elif 'system_design' in skill_tag or 'scaling' in skill_tag:
        return _generate_system_design_template(level, num_days, difficulty)
    elif 'frontend' in skill_tag or 'react' in skill_tag:
        return _generate_frontend_template(skill_tag, level, num_days, difficulty)
    elif 'product' in skill_tag or 'metrics' in skill_tag:
        return _generate_product_template(level, num_days, difficulty)
    elif 'algorithm' in skill_tag or 'technical.algorithms' in skill_tag:
        return _generate_algorithm_template(level, num_days, difficulty)
    else:
        # Generic template
        return _generate_generic_template(skill_tag, level, num_days, difficulty)


def _generate_star_template(level: str, num_days: int, difficulty: str) -> Dict:
    """Generate STAR method template."""
    title = "Master the STAR Method"
    description = "Learn and practice the STAR (Situation, Task, Action, Result) method for answering behavioral interview questions effectively."
    
    steps = []
    if num_days >= 3:
        steps.extend([
            {
                "day": 1,
                "topic": "STAR Framework Basics",
                "drills": [
                    f"Read STAR framework guide ({15 if level == 'junior' else 20} min)",
                    f"Watch {2 if level == 'junior' else 3} example STAR answers ({20 if level == 'junior' else 30} min)",
                    "Identify STAR components in sample answers (15 min)"
                ],
                "mini_mock": "Tell me about a time you handled conflict",
                "quick_test": "Answer 1 question under 90 seconds using STAR"
            },
            {
                "day": 2,
                "topic": "Situation and Task",
                "drills": [
                    f"Write {3 if level == 'junior' else 5} situation statements (15 min)",
                    f"Write {3 if level == 'junior' else 5} task statements (15 min)",
                    "Practice setting context clearly (20 min)"
                ],
                "mini_mock": "Describe a challenging project you worked on",
                "quick_test": "Explain situation and task in 30 seconds"
            },
            {
                "day": 3,
                "topic": "Action - Your Role",
                "drills": [
                    f"Write {3 if level == 'junior' else 5} action statements using 'I' (20 min)",
                    "Practice describing your specific actions (25 min)",
                    "Avoid 'we' language - focus on your contribution (15 min)"
                ],
                "mini_mock": "Tell me about a time you showed leadership",
                "quick_test": "Describe your actions clearly in 45 seconds"
            }
        ])
    
    if num_days >= 5:
        steps.extend([
            {
                "day": 4,
                "topic": "Result - Quantify Impact",
                "drills": [
                    f"Write {3 if level == 'junior' else 5} result statements with metrics (20 min)",
                    "Practice quantifying outcomes (25 min)",
                    "Learn to show impact and learning (15 min)"
                ],
                "mini_mock": "Describe a time you improved a process",
                "quick_test": "Explain results with numbers in 30 seconds"
            },
            {
                "day": 5,
                "topic": "Complete STAR Stories",
                "drills": [
                    f"Write {2 if level == 'junior' else 3} complete STAR stories (30 min)",
                    "Practice timing (90 seconds per story) (25 min)",
                    "Get feedback on structure (20 min)"
                ],
                "mini_mock": "Tell me about a time you failed",
                "quick_test": f"Deliver {1 if level == 'junior' else 2} complete STAR answers under 3 minutes"
            }
        ])
    
    if num_days >= 7:
        steps.extend([
            {
                "day": 6,
                "topic": "Advanced STAR Techniques",
                "drills": [
                    "Practice handling follow-up questions (25 min)",
                    "Learn to adapt STAR for different question types (25 min)",
                    "Practice under pressure (20 min)"
                ],
                "mini_mock": "Answer complex behavioral question",
                "quick_test": "Handle 2 follow-up questions using STAR"
            },
            {
                "day": 7,
                "topic": "STAR Mastery",
                "drills": [
                    "Review all STAR stories (20 min)",
                    "Practice 5 different scenarios (30 min)",
                    "Final mock interview (20 min)"
                ],
                "mini_mock": "Full behavioral interview simulation",
                "quick_test": "Answer 3 questions flawlessly using STAR"
            }
        ])
    
    duration = 45 if level == 'junior' else (60 if level == 'mid' else 70)
    
    return {
        'title': title,
        'description': description,
        'steps_json': steps,
        'difficulty': difficulty,
        'duration_minutes': duration
    }


def _generate_backend_template(skill_tag: str, level: str, num_days: int, difficulty: str) -> Dict:
    """Generate backend/Django template."""
    if 'auth' in skill_tag or 'django.auth' in skill_tag:
        title = "Django Authentication Deep Dive"
        description = "Master Django authentication system including sessions, tokens, and security best practices."
        
        steps = [
            {
                "day": 1,
                "topic": "Django Authentication Basics",
                "drills": [
                    f"Read Django auth documentation ({25 if level == 'junior' else 30} min)",
                    "Understand User model and authentication backends (25 min)",
                    "Practice creating and authenticating users (20 min)"
                ],
                "mini_mock": "Explain how Django authentication works",
                "quick_test": "Implement basic login/logout views"
            },
            {
                "day": 2,
                "topic": "Sessions and Middleware",
                "drills": [
                    "Study session framework (25 min)",
                    "Understand authentication middleware (25 min)",
                    "Practice session management (25 min)"
                ],
                "mini_mock": "How do Django sessions work?",
                "quick_test": "Explain session lifecycle"
            }
        ]
        
        if num_days >= 3:
            steps.append({
                "day": 3,
                "topic": "JWT Tokens",
                "drills": [
                    "Learn JWT token structure (25 min)",
                    f"Implement JWT authentication ({25 if level == 'junior' else 35} min)",
                    "Practice token refresh flow (20 min)"
                ],
                "mini_mock": "Explain JWT authentication flow",
                "quick_test": "Implement JWT login endpoint"
            })
        
        if num_days >= 4:
            steps.append({
                "day": 4,
                "topic": "Permissions and Authorization",
                "drills": [
                    "Study Django permissions system (30 min)",
                    f"Practice {'basic' if level == 'junior' else 'custom'} permissions (25 min)",
                    "Implement role-based access control (25 min)"
                ],
                "mini_mock": "How do you implement permissions in Django?",
                "quick_test": "Create custom permission class"
            })
        
        if num_days >= 5:
            steps.append({
                "day": 5,
                "topic": "Security Best Practices",
                "drills": [
                    "Learn password hashing (20 min)",
                    "Study CSRF protection (25 min)",
                    "Practice secure authentication patterns (30 min)"
                ],
                "mini_mock": "How do you secure Django authentication?",
                "quick_test": "Explain security considerations"
            })
        
        duration = 50 if level == 'junior' else (65 if level == 'mid' else 75)
    else:
        # Generic backend template
        title = f"Backend Development - {skill_tag.split('.')[-1].title()}"
        description = f"Master backend development concepts for {skill_tag}."
        steps = _generate_generic_steps(level, num_days, "backend")
        duration = 45 if level == 'junior' else (60 if level == 'mid' else 70)
    
    return {
        'title': title,
        'description': description,
        'steps_json': steps[:num_days],
        'difficulty': difficulty,
        'duration_minutes': duration
    }


def _generate_sql_template(level: str, num_days: int, difficulty: str) -> Dict:
    """Generate SQL template."""
    title = "SQL Joins Mastery"
    description = "Master SQL joins including inner, left, right, full outer joins and complex query optimization."
    
    steps = [
        {
            "day": 1,
            "topic": "Join Types Fundamentals",
            "drills": [
                "Review INNER JOIN syntax (20 min)",
                f"Practice {3 if level == 'junior' else 5} INNER JOIN queries (30 min)",
                "Understand when to use each join type (20 min)"
            ],
            "mini_mock": "Explain the difference between INNER and LEFT JOIN",
            "quick_test": "Write 3 JOIN queries"
        },
        {
            "day": 2,
            "topic": "LEFT and RIGHT Joins",
            "drills": [
                f"Practice LEFT JOIN queries ({25 if level == 'junior' else 35} min)",
                "Practice RIGHT JOIN queries (20 min)",
                f"Solve {3 if level == 'junior' else 5} problems with LEFT JOIN (25 min)"
            ],
            "mini_mock": "When would you use LEFT JOIN vs INNER JOIN?",
            "quick_test": "Write LEFT JOIN query for user orders"
        }
    ]
    
    if num_days >= 3:
        steps.append({
            "day": 3,
            "topic": "Multiple Table Joins",
            "drills": [
                f"Practice joining {2 if level == 'junior' else 3}+ tables (35 min)",
                "Optimize join order (25 min)",
                f"Solve {'simple' if level == 'junior' else 'complex'} join problems (20 min)"
            ],
            "mini_mock": "Join users, orders, and products tables",
            "quick_test": f"Write query joining {3 if level == 'junior' else 4} tables"
        })
    
    if num_days >= 4:
        steps.append({
            "day": 4,
            "topic": "Join Performance",
            "drills": [
                "Learn about join indexes (25 min)",
                f"Practice query optimization ({25 if level == 'junior' else 35} min)",
                "Analyze execution plans (20 min)"
            ],
            "mini_mock": "How do you optimize JOIN queries?",
            "quick_test": "Optimize a slow JOIN query"
        })
    
    duration = 45 if level == 'junior' else (55 if level == 'mid' else 65)
    
    return {
        'title': title,
        'description': description,
        'steps_json': steps[:num_days],
        'difficulty': difficulty,
        'duration_minutes': duration
    }


def _generate_system_design_template(level: str, num_days: int, difficulty: str) -> Dict:
    """Generate system design template."""
    title = "System Design Scaling"
    description = "Learn horizontal and vertical scaling, load balancing, caching strategies, and distributed systems."
    
    steps = [
        {
            "day": 1,
            "topic": "Scaling Fundamentals",
            "drills": [
                "Read about horizontal vs vertical scaling (25 min)",
                "Study load balancing concepts (30 min)",
                f"Practice designing {'basic' if level == 'junior' else 'scalable'} architectures (25 min)"
            ],
            "mini_mock": "Explain horizontal vs vertical scaling",
            "quick_test": "Design a scalable web service"
        },
        {
            "day": 2,
            "topic": "Caching Strategies",
            "drills": [
                "Learn caching patterns (CDN, Redis, Memcached) (35 min)",
                "Practice cache invalidation strategies (25 min)",
                "Design caching layer (20 min)"
            ],
            "mini_mock": "How would you implement caching?",
            "quick_test": "Design cache strategy for API"
        }
    ]
    
    if num_days >= 3:
        steps.append({
            "day": 3,
            "topic": "Database Scaling",
            "drills": [
                "Study database replication (30 min)",
                f"Learn {'basic' if level == 'junior' else 'advanced'} sharding strategies (30 min)",
                "Practice read/write splitting (20 min)"
            ],
            "mini_mock": "How do you scale a database?",
            "quick_test": "Design sharding strategy"
        })
    
    if num_days >= 4:
        steps.append({
            "day": 4,
            "topic": "Microservices Architecture",
            "drills": [
                "Learn microservices patterns (35 min)",
                "Study service communication (25 min)",
                "Practice designing microservices (20 min)"
            ],
            "mini_mock": "When would you use microservices?",
            "quick_test": "Design microservices architecture"
        })
    
    duration = 60 if level == 'junior' else (75 if level == 'mid' else 90)
    
    return {
        'title': title,
        'description': description,
        'steps_json': steps[:num_days],
        'difficulty': difficulty,
        'duration_minutes': duration
    }


def _generate_frontend_template(skill_tag: str, level: str, num_days: int, difficulty: str) -> Dict:
    """Generate frontend/React template."""
    if 'hooks' in skill_tag or 'react.hooks' in skill_tag:
        title = "React Hooks Mastery"
        description = "Master React hooks including useState, useEffect, useContext, and custom hooks patterns."
        
        steps = [
            {
                "day": 1,
                "topic": "useState and useEffect",
                "drills": [
                    f"Review useState hook ({15 if level == 'junior' else 25} min)",
                    f"Practice useEffect patterns ({25 if level == 'junior' else 35} min)",
                    "Build component with hooks (25 min)"
                ],
                "mini_mock": "Explain useState and useEffect",
                "quick_test": "Build counter component with hooks"
            },
            {
                "day": 2,
                "topic": "useContext and useReducer",
                "drills": [
                    "Learn useContext for state management (30 min)",
                    f"Practice useReducer pattern ({20 if level == 'junior' else 30} min)",
                    "Build context provider (25 min)"
                ],
                "mini_mock": "When would you use useContext vs props?",
                "quick_test": "Implement context with hooks"
            }
        ]
        
        if num_days >= 3:
            steps.append({
                "day": 3,
                "topic": "Custom Hooks",
                "drills": [
                    "Learn custom hook patterns (30 min)",
                    f"Practice creating reusable hooks ({25 if level == 'junior' else 35} min)",
                    f"Build {2 if level == 'junior' else 3} custom hooks (30 min)"
                ],
                "mini_mock": "Create a custom hook for API calls",
                "quick_test": "Build custom useFetch hook"
            })
        
        duration = 50 if level == 'junior' else (60 if level == 'mid' else 70)
    else:
        title = f"Frontend Development - {skill_tag.split('.')[-1].title()}"
        description = f"Master frontend development concepts for {skill_tag}."
        steps = _generate_generic_steps(level, num_days, "frontend")
        duration = 45 if level == 'junior' else (60 if level == 'mid' else 70)
    
    return {
        'title': title,
        'description': description,
        'steps_json': steps[:num_days],
        'difficulty': difficulty,
        'duration_minutes': duration
    }


def _generate_product_template(level: str, num_days: int, difficulty: str) -> Dict:
    """Generate product metrics template."""
    title = "Product Metrics and KPIs"
    description = "Learn to define, track, and analyze product metrics including user engagement, retention, and business KPIs."
    
    steps = [
        {
            "day": 1,
            "topic": "Core Product Metrics",
            "drills": [
                "Learn DAU, MAU, retention metrics (30 min)",
                "Study conversion funnel metrics (25 min)",
                "Practice calculating key metrics (25 min)"
            ],
            "mini_mock": "What metrics would you track for a social app?",
            "quick_test": "Define 5 key metrics for a product"
        },
        {
            "day": 2,
            "topic": "User Engagement Metrics",
            "drills": [
                "Study engagement metrics (session length, frequency) (30 min)",
                f"Learn {'basic' if level == 'junior' else 'advanced'} cohort analysis (30 min)",
                "Practice analyzing user behavior (20 min)"
            ],
            "mini_mock": "How do you measure user engagement?",
            "quick_test": "Analyze user engagement data"
        }
    ]
    
    if num_days >= 3:
        steps.append({
            "day": 3,
            "topic": "Business Metrics",
            "drills": [
                "Learn revenue metrics (ARPU, LTV, CAC) (35 min)",
                "Study growth metrics (25 min)",
                "Practice calculating business KPIs (20 min)"
            ],
            "mini_mock": "Explain LTV and CAC",
            "quick_test": "Calculate key business metrics"
        })
    
    duration = 45 if level == 'junior' else (55 if level == 'mid' else 65)
    
    return {
        'title': title,
        'description': description,
        'steps_json': steps[:num_days],
        'difficulty': difficulty,
        'duration_minutes': duration
    }


def _generate_algorithm_template(level: str, num_days: int, difficulty: str) -> Dict:
    """Generate algorithm template."""
    title = "Algorithm Problem-Solving"
    description = "Master algorithm problem-solving techniques including time/space complexity, common patterns, and practice strategies."
    
    steps = [
        {
            "day": 1,
            "topic": "Time and Space Complexity",
            "drills": [
                f"Review Big O notation ({20 if level == 'junior' else 30} min)",
                "Practice analyzing complexity (30 min)",
                f"Solve {2 if level == 'junior' else 3} problems analyzing complexity (20 min)"
            ],
            "mini_mock": "Explain time complexity of binary search",
            "quick_test": "Analyze complexity of 3 algorithms"
        },
        {
            "day": 2,
            "topic": "Common Patterns - Two Pointers",
            "drills": [
                "Learn two pointers pattern (25 min)",
                f"Solve {3 if level == 'junior' else 5} two pointer problems (35 min)",
                "Practice variations (20 min)"
            ],
            "mini_mock": "Solve two sum problem",
            "quick_test": "Implement two pointers solution"
        }
    ]
    
    if num_days >= 3:
        steps.append({
            "day": 3,
            "topic": "Common Patterns - Sliding Window",
            "drills": [
                "Learn sliding window pattern (25 min)",
                f"Solve {3 if level == 'junior' else 5} sliding window problems (35 min)",
                "Practice optimization (20 min)"
            ],
            "mini_mock": "Find longest substring without repeating characters",
            "quick_test": "Implement sliding window solution"
        })
    
    if num_days >= 4:
        steps.append({
            "day": 4,
            "topic": "Hash Maps and Sets",
            "drills": [
                "Review hash map operations (20 min)",
                f"Solve {3 if level == 'junior' else 5} hash map problems (35 min)",
                "Practice set operations (25 min)"
            ],
            "mini_mock": "When would you use a hash map?",
            "quick_test": "Solve problem using hash map"
        })
    
    duration = 50 if level == 'junior' else (65 if level == 'mid' else 80)
    
    return {
        'title': title,
        'description': description,
        'steps_json': steps[:num_days],
        'difficulty': difficulty,
        'duration_minutes': duration
    }


def _generate_generic_template(skill_tag: str, level: str, num_days: int, difficulty: str) -> Dict:
    """Generate generic template for unknown skill tags."""
    skill_name = skill_tag.split('.')[-1].replace('_', ' ').title()
    title = f"Master {skill_name}"
    description = f"Learn and practice {skill_name} concepts and techniques."
    
    steps = _generate_generic_steps(level, num_days, skill_tag.split('.')[0])
    
    duration = 45 if level == 'junior' else (60 if level == 'mid' else 75)
    
    return {
        'title': title,
        'description': description,
        'steps_json': steps,
        'difficulty': difficulty,
        'duration_minutes': duration
    }


def _generate_generic_steps(level: str, num_days: int, category: str) -> List[Dict]:
    """Generate generic daily steps."""
    steps = []
    
    for day in range(1, num_days + 1):
        if day == 1:
            topic = "Fundamentals"
            drills = [
                f"Read documentation ({20 if level == 'junior' else 30} min)",
                "Understand core concepts (25 min)",
                "Practice basic examples (20 min)"
            ]
        elif day == 2:
            topic = "Practice and Application"
            drills = [
                f"Solve {3 if level == 'junior' else 5} practice problems (30 min)",
                "Review solutions (20 min)",
                "Identify patterns (15 min)"
            ]
        elif day == 3:
            topic = "Advanced Concepts"
            drills = [
                f"Study {'intermediate' if level == 'junior' else 'advanced'} topics (30 min)",
                "Practice complex scenarios (25 min)",
                "Apply to real-world examples (20 min)"
            ]
        else:
            topic = f"Day {day} - Deep Dive"
            drills = [
                f"Review previous concepts (15 min)",
                f"Practice {category} problems (30 min)",
                "Build practical examples (25 min)"
            ]
        
        steps.append({
            "day": day,
            "topic": topic,
            "drills": drills,
            "mini_mock": f"Practice {category} question",
            "quick_test": f"Complete {category} exercise"
        })
    
    return steps

