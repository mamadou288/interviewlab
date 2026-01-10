# Profiles Module Documentation

## Overview

CV/Resume parsing and profile management module. Handles CV document uploads, text extraction from PDF/DOCX files, structured data extraction (experience, skills, education, projects), and profile data management. Supports multi-language CV parsing.

## Models

### CVDocument (`backend/profiles/models/cvdocument.py`)
Stores uploaded CV files and processing status.

**Fields:** `id` (UUID), `user` (FK → User), `file` (FileField), `status` ('uploaded'|'processing'|'completed'|'failed'), `extracted_text` (TextField), `file_size`, `mime_type`, timestamps

**Validation:** Max 10MB, PDF/DOCX only (configurable via `MAX_UPLOAD_SIZE`, `ALLOWED_FILE_TYPES`)

### Profile (`backend/profiles/models/profile.py`)
Stores structured profile data extracted from CVs.

**Fields:** `id` (UUID), `user` (OneToOne → User), `cv_document` (FK → CVDocument), `data_json` (JSONField), `confirmed` (Boolean), timestamps

**data_json structure:**
```json
{
  "experience": [{"title": "...", "company": "...", "dates": "...", "description": "..."}],
  "skills": ["Python", "Django"],
  "education": [{"degree": "...", "institution": "...", "dates": "..."}],
  "projects": [{"name": "...", "description": "...", "technologies": [...]}]
}
```

## API Endpoints

Base path: `/api/`

### POST `/api/cv/upload`
Upload CV (PDF/DOCX). Extracts text, parses data, creates/updates profile.

**Headers:** `Authorization: Bearer <token>`  
**Request:** Multipart form data with `file` field  
**Response:** CVDocument with status, file_url, timestamps

**Flow:** Validate → Extract text → Parse data → Update Profile → Set status 'completed'

### GET `/api/cv/{id}`
Get CV document details. **Headers:** `Authorization: Bearer <token>`

### GET `/api/profile/me`
Get current user's profile. **Headers:** `Authorization: Bearer <token>`  
**Response:** Profile with nested cv_document and data_json

### PATCH `/api/profile/me`
Update profile data (confirm or edit). **Headers:** `Authorization: Bearer <token>`  
**Request:** `{"data_json": {...}, "confirmed": true}`

## Services

### Parser Service (`backend/profiles/services/parser.py`)
- `validate_file(file)`: Validates type and size
- `extract_text_pdf(file)`: Uses `pdfplumber`
- `extract_text_docx(file)`: Uses `python-docx`
- `extract_text(file)`: Routes to appropriate extractor

### Extractor Service (`backend/profiles/services/extractor.py`)
- `extract_profile_data(text)`: Extracts structured data using regex patterns

**Extraction:** Experience (job titles, companies, dates), Skills (technical skills, tools), Education (degrees, institutions), Projects (names, descriptions, technologies)

**Multi-language support:** English, French, Spanish, German, Arabic, Portuguese, Italian

## Serializers

- **`CVDocumentSerializer`**: id, user, file, status, file_size, mime_type, timestamps, file_url
- **`ProfileSerializer`**: id, user, cv_document (nested), data_json, confirmed, timestamps
- **`ProfileUpdateSerializer`**: data_json, confirmed

## Configuration

```python
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
```

## Permissions

- `IsAuthenticated`: Required for all endpoints
- `IsAuthenticatedOwner`: Users can only access their own CV documents

## Usage

```python
from profiles.models import CVDocument, Profile
from profiles.services.parser import extract_text
from profiles.services.extractor import extract_profile_data

# Get profile
profile = Profile.objects.get(user=request.user)
experience = profile.data_json.get('experience', [])

# Extract data
text = extract_text(file)
data = extract_profile_data(text)
```

## File Structure

```
backend/profiles/
├── models/ (cvdocument.py, profile.py)
├── serializers/ (cvdocument.py, profile.py)
├── services/ (parser.py, extractor.py)
├── views/ (cv.py, profile.py)
├── urls.py
└── admin.py
```
