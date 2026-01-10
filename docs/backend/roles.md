# Roles Module Documentation

## Overview

Role catalog and suggestion engine module. Manages job roles catalog and provides intelligent role suggestions based on CV/profile data using keyword matching and scoring algorithms.

## Models

### RoleCatalog (`backend/roles/models/role_catalog.py`)
Stores predefined job roles with categories and keywords.

**Fields:** `id` (UUID), `name` (unique), `category` ('backend'|'frontend'|'fullstack'|'devops'|'data'|'product'|'design'|'mobile'|'qa'|'other'), `keywords_json` (list), `description`, `level_keywords_json` (dict), timestamps

**keywords_json example:** `["python", "django", "api", "rest", "postgresql"]`

### RoleSuggestion (`backend/roles/models/role_suggestion.py`)
Stores role suggestions for CV documents with scores and reasons.

**Fields:** `id` (UUID), `cv_document` (FK → CVDocument), `role` (FK → RoleCatalog), `score` (0.00-1.00), `reasons_json` (list), `created_at`

**Constraints:** `unique_together`: ['cv_document', 'role']

## API Endpoints

Base path: `/api/`

### GET `/api/roles`
List and search roles. **Headers:** `Authorization: Bearer <token>`

**Query params:** `category` (filter), `search` (name/description)  
**Response:** List of roles with id, name, category, keywords_json, description

### GET `/api/cv/{cv_id}/role-suggestions`
Get role suggestions for CV. Generates if don't exist. **Headers:** `Authorization: Bearer <token>`

**Response:** List of suggestions with role (nested), score, reasons_json, sorted by score

**Flow:** Check existing → Generate if needed → Extract keywords → Calculate scores → Generate reasons → Store top 10

## Suggestion Engine

### Service (`backend/roles/services/suggester.py`)

**`extract_profile_keywords(profile_data)`**: Extracts from skills, job titles, projects → normalized keyword list

**`calculate_role_score(profile_keywords, role)`**: Calculates similarity (0.0-1.0)
- Title match: +0.3
- Skill matches: +0.1 per match (max 0.5)
- Keyword matches: +0.05 per match (max 0.2)
- Normalized to 0.0-1.0

**`generate_reasons(profile_data, role, score)`**: Generates human-readable reasons (max 3)
- Counts matched skills
- Checks experience relevance
- Checks role name in experience titles

**`suggest_roles(cv_document_id)`**: Main function
1. Get CVDocument and Profile
2. Extract keywords
3. Calculate scores for all roles
4. Sort by score
5. Generate reasons for top matches
6. Create/update RoleSuggestion records (top 10)
7. Return suggestions

## Role Catalog Fixtures

Loaded from `backend/roles/fixtures/roles.json`: Backend Engineer, Frontend Developer, Full-stack Developer, DevOps Engineer, Data Scientist, Data Engineer, Product Manager, Mobile Developer (iOS/Android), QA Engineer, UI/UX Designer, Backend/Frontend Architect, ML Engineer, Security Engineer

**Load:** `python manage.py loaddata roles/fixtures/roles.json`

## Serializers

- **`RoleCatalogSerializer`**: id, name, category, keywords_json, description, level_keywords_json, timestamps
- **`RoleSuggestionSerializer`**: id, role (nested), score, reasons_json, created_at

## Permissions

- `IsAuthenticated`: Required for all endpoints
- `IsAuthenticatedOwner`: Users can only access suggestions for their own CVs

## Usage

```python
from roles.models import RoleCatalog, RoleSuggestion
from roles.services.suggester import suggest_roles

# Get roles
roles = RoleCatalog.objects.filter(category='backend')

# Generate suggestions
suggestions = suggest_roles(cv_document_id)

# Get top suggestion
top = RoleSuggestion.objects.filter(cv_document=cv_doc).order_by('-score').first()
```

## File Structure

```
backend/roles/
├── models/ (role_catalog.py, role_suggestion.py)
├── serializers/ (role_catalog.py, role_suggestion.py)
├── services/ (suggester.py)
├── fixtures/ (roles.json)
├── views/ (catalog.py, suggestions.py)
├── urls.py
└── admin.py
```
