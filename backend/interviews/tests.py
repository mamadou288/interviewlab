from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import InterviewSession, InterviewQuestion, InterviewAnswer
from roles.models import RoleCatalog
from profiles.models import Profile

User = get_user_model()


class InterviewSessionTests(TestCase):
    """Test interview session creation and management."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        
        # Create role
        self.role = RoleCatalog.objects.create(
            name='Backend Engineer',
            category='backend',
            description='Backend development role',
            keywords_json=['python', 'django'],
            level_keywords_json={'junior': ['python'], 'mid': ['django'], 'senior': ['architecture']}
        )
        
        # Create profile
        self.profile = Profile.objects.create(
            user=self.user,
            data_json={'skills': ['Python', 'Django']}
        )
    
    def test_create_interview_session(self):
        """Test creating an interview session."""
        data = {
            'role_id': str(self.role.id),
            'level': 'mid',
            'type': 'technical',
        }
        response = self.client.post('/api/interviews', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertEqual(response.data['type'], 'technical')
        
        # Verify session was created
        session = InterviewSession.objects.get(id=response.data['id'])
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.role_selected, self.role)
        self.assertEqual(session.level, 'mid')
        
        # Verify questions were generated
        questions = InterviewQuestion.objects.filter(session=session)
        self.assertGreater(questions.count(), 0)
    
    def test_get_interview_session(self):
        """Test retrieving an interview session."""
        session = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='technical',
            status='in_progress'
        )
        
        url = f'/api/interviews/{session.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(session.id))
        self.assertEqual(response.data['status'], 'in_progress')
    
    def test_get_interview_questions(self):
        """Test retrieving interview questions."""
        session = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='technical',
            status='in_progress'
        )
        
        # Create test questions
        question1 = InterviewQuestion.objects.create(
            session=session,
            order=1,
            question_text='What is Django?',
            category='technical',
            difficulty='medium',
            skill_tags_json=['backend.django.auth']
        )
        question2 = InterviewQuestion.objects.create(
            session=session,
            order=2,
            question_text='Explain REST API',
            category='technical',
            difficulty='medium',
            skill_tags_json=['backend.api.rest']
        )
        
        url = f'/api/interviews/{session.id}/questions'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('questions', response.data)
        self.assertEqual(len(response.data['questions']), 2)


class InterviewAnswerTests(TestCase):
    """Test interview answer submission and scoring."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        
        # Create role
        self.role = RoleCatalog.objects.create(
            name='Backend Engineer',
            category='backend',
            description='Backend development role',
            keywords_json=['python', 'django'],
            level_keywords_json={'junior': ['python'], 'mid': ['django'], 'senior': ['architecture']}
        )
        
        # Create session
        self.session = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='technical',
            status='in_progress'
        )
        
        # Create question
        self.question = InterviewQuestion.objects.create(
            session=self.session,
            order=1,
            question_text='What is Django?',
            category='technical',
            difficulty='medium',
            skill_tags_json=['backend.django.auth']
        )
    
    def test_submit_answer(self):
        """Test submitting an answer."""
        data = {
            'question_id': str(self.question.id),
            'answer_text': 'Django is a high-level Python web framework.',
            'time_seconds': 120,
        }
        url = f'/api/interviews/{self.session.id}/answers'
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('scores_json', response.data)
        self.assertIn('feedback_json', response.data)
        
        # Verify answer was created
        answer = InterviewAnswer.objects.get(id=response.data['id'])
        self.assertEqual(answer.question, self.question)
        self.assertIn('structure', answer.scores_json)
        self.assertIn('strengths', answer.feedback_json)
    
    def test_finish_session(self):
        """Test finishing an interview session."""
        # Create some answers first
        question2 = InterviewQuestion.objects.create(
            session=self.session,
            order=2,
            question_text='Explain REST API',
            category='technical',
            difficulty='medium',
            skill_tags_json=['backend.api.rest']
        )
        
        # Submit answers
        answer1_data = {
            'question_id': str(self.question.id),
            'answer_text': 'Django is a web framework.',
            'time_seconds': 120,
        }
        self.client.post(f'/api/interviews/{self.session.id}/answers', answer1_data, format='json')
        
        answer2_data = {
            'question_id': str(question2.id),
            'answer_text': 'REST is an architectural style.',
            'time_seconds': 90,
        }
        self.client.post(f'/api/interviews/{self.session.id}/answers', answer2_data, format='json')
        
        # Finish session
        url = f'/api/interviews/{self.session.id}/finish'
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertIsNotNone(response.data['overall_score'])
        self.assertIn('ended_at', response.data)
        
        # Verify session was updated
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, 'completed')
        self.assertIsNotNone(self.session.overall_score)
    
    def test_get_report(self):
        """Test getting interview report."""
        # Create answer
        answer = InterviewAnswer.objects.create(
            question=self.question,
            answer_text='Django is a web framework.',
            time_seconds=120,
            scores_json={
                'structure': 4,
                'relevance': 5,
                'technical_accuracy': 4,
                'depth': 3,
                'communication': 4,
            },
            feedback_json={
                'strengths': ['Clear explanation'],
                'weaknesses': ['Could add more detail'],
            },
            skill_tags_json=['backend.django.auth']
        )
        
        # Finish session
        self.session.status = 'completed'
        self.session.overall_score = 80
        self.session.save()
        
        url = f'/api/interviews/{self.session.id}/report'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('session', response.data)
        self.assertIn('strengths', response.data)
        self.assertIn('weaknesses', response.data)
        self.assertIn('rubric_breakdown', response.data)
        self.assertIn('skill_breakdown', response.data)


class ScoringServiceTests(TestCase):
    """Test scoring service logic."""
    
    def test_score_answer(self):
        """Test scoring an answer."""
        from .services.scorer import score_answer
        from .models import InterviewQuestion
        
        question = InterviewQuestion(
            question_text='What is Django?',
            category='technical',
            difficulty='medium',
            skill_tags_json=['backend.django.auth']
        )
        
        answer_text = 'Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.'
        
        scores = score_answer(answer_text, question)
        
        # Check all dimensions are scored
        self.assertIn('structure', scores)
        self.assertIn('relevance', scores)
        self.assertIn('technical_accuracy', scores)
        self.assertIn('depth', scores)
        self.assertIn('communication', scores)
        
        # Check scores are in valid range (0-5)
        for dimension, score in scores.items():
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 5)


class FeedbackServiceTests(TestCase):
    """Test feedback generation service."""
    
    def test_generate_feedback(self):
        """Test generating feedback for an answer."""
        from .services.feedback import generate_feedback
        from .models import InterviewQuestion
        
        question = InterviewQuestion(
            question_text='What is Django?',
            category='technical',
            difficulty='medium',
            skill_tags_json=['backend.django.auth']
        )
        
        answer_text = 'Django is a web framework.'
        scores = {
            'structure': 4,
            'relevance': 5,
            'technical_accuracy': 4,
            'depth': 2,
            'communication': 4,
        }
        
        feedback = generate_feedback(answer_text, scores, question)
        
        self.assertIn('strengths', feedback)
        self.assertIn('weaknesses', feedback)
        self.assertIn('improvements', feedback)
        self.assertIsInstance(feedback['strengths'], list)
        self.assertIsInstance(feedback['weaknesses'], list)
