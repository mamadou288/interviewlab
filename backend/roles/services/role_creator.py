"""
Service to find or create roles dynamically based on CV data.
"""
from typing import Optional, Tuple
from ..models import RoleCatalog


def find_or_create_role(role_name: str, category: str = 'other', skills: list = None) -> Tuple[RoleCatalog, bool]:
    """
    Find an existing role or create a new one based on CV data.
    
    Args:
        role_name: The role name extracted from CV
        category: Role category (it, marketing, sales, etc.)
        skills: List of skills to use as keywords
        
    Returns:
        Tuple of (RoleCatalog instance, created boolean)
    """
    if not role_name:
        return None, False
    
    # Normalize role name
    role_name = role_name.strip()
    
    # Try to find exact match first
    try:
        role = RoleCatalog.objects.get(name__iexact=role_name)
        return role, False
    except RoleCatalog.DoesNotExist:
        pass
    
    # Try to find similar role (case-insensitive partial match)
    similar_roles = RoleCatalog.objects.filter(name__icontains=role_name)
    if similar_roles.exists():
        # Return the first similar match
        return similar_roles.first(), False
    
    # Create new role if not found
    # Map category to RoleCatalog category choices
    category_mapping = {
        'it': 'backend',  # Default IT to backend
        'marketing': 'other',
        'sales': 'other',
        'finance': 'other',
        'hr': 'other',
        'design': 'design',
        'data': 'data',
        'product': 'product',
        'operations': 'other',
        'other': 'other',
    }
    
    catalog_category = category_mapping.get(category.lower(), 'other')
    
    # Extract keywords from skills if provided
    keywords = []
    if skills:
        keywords = [skill.lower() for skill in skills[:20]]  # Limit to 20 keywords
    
    # Create the role
    role = RoleCatalog.objects.create(
        name=role_name,
        category=catalog_category,
        keywords_json=keywords,
        description=f"Role extracted from CV: {role_name}",
        level_keywords_json={}
    )
    
    return role, True

