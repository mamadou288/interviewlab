# Interviews Module Documentation

## Overview

Interview session management module. Handles session creation, question generation, answer submission, automated scoring (5-dimension rubric), feedback generation, and session reporting. Supports HR, Technical, Case Study, and Mixed interview types with role-based question selection.

## Models

### InterviewSession (`backend/interviews/models/interview_session.py`)
Stores interview session information and status.

**Fields:** `id` (UUID), `user` (FK → User), `profile` (FK → Profile, nullable), `role_selected` (FK → RoleCatalog), `role_source` ('suggestion'|'catalog'|'custom'), `level` ('junior'|'mid'|'senior'), `type` ('hr'|'technical'|'case'|'mixed'), `status` ('created'|'in_progress'|'completed'|'abandoned'), `overall_score` (0-100, nullable), `started_at`, `ended_at` (nullable), timestamps

### InterviewQuestion (`backend/interviews/models/interview_question.py`)
Stores questions for a session.

**Fields:** `id` (UUID), `session` (FK → InterviewSession), `order` (int), `question_text`, `category` ('hr'|'technical'|'case'|'behavioral'), `difficulty` ('easy'|'medium'|'hard'), `skill_tags_json` (list), `is_followup` (bool), `parent_question` (FK → self, nullable), `created_at`

**Constraints:** `unique_together`: ['session', 'order']

### InterviewAnswer (`backend/interviews/models/interview_answer.py`)
Stores answers with scores and feedback.

**Fields:** `id` (UUID), `question` (OneToOne → InterviewQuestion), `answer_text`, `submitted_at`, `time_seconds`, `scores_json` (dict: structure, relevance, technical_accuracy, depth, communication - each 0-5), `feedback_json` (dict: strengths, weaknesses, model_answer, improvements), `skill_tags_json` (list), `created_at`

## API Endpoints

Base path: `/api/`

### POST `/api/interviews`
Create session and generate questions. **Headers:** `Authorization: Bearer <token>`

**Request:** `{"role_id": "uuid", "level": "mid", "type": "technical", "profile_id": "uuid" (optional)}`  
**Response:** Session with role_selected (nested), status, progress (current_question, total_questions, answered)

**Flow:** Validate → Create session → Generate 10-15 questions → Set status 'in_progress'

### GET `/api/interviews/{id}`
Get session details with progress. **Headers:** `Authorization: Bearer <token>`

### GET `/api/interviews/{id}/questions`
Get all questions. **Headers:** `Authorization: Bearer <token>`  
**Response:** List of questions with order, question_text, category, difficulty, skill_tags_json

### POST `/api/interviews/{id}/answers`
Submit answer, get scores/feedback. **Headers:** `Authorization: Bearer <token>`

**Request:** `{"question_id": "uuid", "answer_text": "...", "time_seconds": 120}`  
**Response:** Answer with question (nested), scores_json, feedback_json

**Flow:** Validate → Score answer (5 dimensions) → Generate feedback → Create answer → Return with scores/feedback

### POST `/api/interviews/{id}/finish`
Finish session, calculate overall score. **Headers:** `Authorization: Bearer <token>`  
**Response:** Session with status 'completed', overall_score, ended_at

### GET `/api/interviews/{id}/report`
Get comprehensive report. **Headers:** `Authorization: Bearer <token>`  
**Response:** Session info, strengths (top 3), weaknesses (top 3-5), rubric_breakdown (averages), skill_breakdown (by tag), answer summaries

## Services

### Question Generation (`backend/interviews/services/generator.py`)
- `select_questions(role, level, type, profile_data)`: Selects 10-15 questions from bank
- `distribute_questions(questions, type)`: Ensures proper distribution (HR: 40% behavioral, 30% situational, 30% role-specific; Technical: 50% core, 30% advanced, 20% practical; Case: 60% problem-solving, 40% system design; Mixed: balanced)
- `assign_skill_tags(questions, role)`: Assigns skill tags based on role
- `generate_interview_questions(session_id)`: Main function - creates InterviewQuestion records

### Scoring (`backend/interviews/services/scorer.py`)
**5-dimension rubric (0-5 each):**
- `score_structure`: STAR format, logical flow, length
- `score_relevance`: Addresses question
- `score_technical_accuracy`: Technical terms, concepts
- `score_depth`: Detail level, examples, tradeoffs
- `score_communication`: Clarity, readability

**`score_answer(answer_text, question)`**: Scores all dimensions  
**`calculate_overall_score(scores)`**: Weighted average → 0-100 scale (structure*0.2 + relevance*0.2 + technical_accuracy*0.25 + depth*0.2 + communication*0.15) * 20

### Feedback (`backend/interviews/services/feedback.py`)
- `generate_strengths(scores, answer_text, question)`: Top 3 strengths
- `generate_weaknesses(scores, answer_text, question)`: Top 3-5 weaknesses
- `generate_model_answer(question)`: Reference answer template
- `generate_improvements(weaknesses)`: Actionable suggestions
- `generate_feedback(answer_text, scores, question)`: Complete feedback dict

### Report (`backend/interviews/services/report.py`)
- `aggregate_scores(session)`: Average scores per dimension
- `identify_strengths(session)`: Top 3 from all answers
- `identify_weaknesses(session)`: Top 3-5 from all answers
- `calculate_skill_breakdown(session)`: Average scores by skill_tag
- `generate_report(session_id)`: Complete report dict

## Scoring Rubric

**Structure (0-5):** 0-1: No structure; 2: Some organization; 3: Clear structure; 4: Well-structured; 5: Excellent  
**Relevance (0-5):** 0-1: Off-topic; 2: Partially relevant; 3: Addresses question; 4: Direct answer; 5: Perfect  
**Technical Accuracy (0-5):** 0-1: Major errors; 2: Some correct; 3: Mostly correct; 4: Accurate; 5: Perfect  
**Depth (0-5):** 0-1: Surface; 2: Basic; 3: Good details; 4: Detailed with tradeoffs; 5: Comprehensive  
**Communication (0-5):** 0-1: Unclear; 2: Understandable; 3: Clear; 4: Concise; 5: Excellent

## Serializers

- **`InterviewSessionSerializer`**: id, user, profile, role_selected (nested), role_source, level, type, status, overall_score, timestamps, progress
- **`InterviewQuestionSerializer`**: id, session, order, question_text, category, difficulty, skill_tags_json, is_followup, parent_question, created_at
- **`InterviewAnswerSerializer`**: question_id, answer_text, time_seconds (for submission)
- **`InterviewAnswerResponseSerializer`**: id, question (nested), answer_text, scores_json, feedback_json, skill_tags_json, submitted_at, time_seconds

## Permissions

- `IsAuthenticated`: Required for all endpoints
- `IsAuthenticatedOwner`: Users can only access their own sessions

## Usage

```python
from interviews.models import InterviewSession, InterviewQuestion, InterviewAnswer
from interviews.services.scorer import score_answer, calculate_overall_score
from interviews.services.report import generate_report

# Get session
session = InterviewSession.objects.get(id=session_id)
questions = session.questions.all()

# Score answer
scores = score_answer(answer_text, question)
overall = calculate_overall_score(scores)

# Generate report
report = generate_report(session_id)
```

## File Structure

```
backend/interviews/
├── models/ (interview_session.py, interview_question.py, interview_answer.py)
├── serializers/ (interview_session.py, interview_question.py, interview_answer.py)
├── services/ (generator.py, scorer.py, feedback.py, report.py)
├── views/ (session.py, questions.py, answers.py, report.py)
├── urls.py
└── admin.py
```
