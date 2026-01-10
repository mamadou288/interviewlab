from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from interviews.models import InterviewSession, InterviewQuestion, InterviewAnswer
from roles.models import RoleCatalog
from profiles.models import Profile
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class AnalyticsOverviewTests(TestCase):
    """Test analytics overview endpoint."""
    
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
        
        # Create completed sessions
        self.session1 = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='technical',
            status='completed',
            overall_score=70,
            started_at=timezone.now() - timedelta(days=10),
            ended_at=timezone.now() - timedelta(days=10)
        )
        
        self.session2 = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='hr',
            status='completed',
            overall_score=80,
            started_at=timezone.now() - timedelta(days=5),
            ended_at=timezone.now() - timedelta(days=5)
        )
        
        # Create questions and answers
        question1 = InterviewQuestion.objects.create(
            session=self.session1,
            order=1,
            question_text='What is Django?',
            category='technical',
            difficulty='medium',
            skill_tags_json=['backend.django.auth']
        )
        
        InterviewAnswer.objects.create(
            question=question1,
            answer_text='Django is a web framework.',
            time_seconds=120,
            scores_json={
                'structure': 3,
                'relevance': 4,
                'technical_accuracy': 3,
                'depth': 2,
                'communication': 3,
            },
            feedback_json={
                'strengths': ['Clear'],
                'weaknesses': ['Needs depth'],
            },
            skill_tags_json=['backend.django.auth']
        )
    
    def test_get_overview(self):
        """Test getting analytics overview."""
        response = self.client.get('/api/analytics/overview')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('overall_score', response.data)
        self.assertIn('total_sessions', response.data)
        self.assertIn('score_trend', response.data)
        self.assertIn('category_trend', response.data)
        self.assertIn('top_improving_skills', response.data)
        self.assertIn('top_weak_skills', response.data)
        
        # Check data types
        self.assertIsInstance(response.data['overall_score'], (int, float))
        self.assertIsInstance(response.data['total_sessions'], int)
        self.assertIsInstance(response.data['score_trend'], list)
        self.assertIsInstance(response.data['category_trend'], dict)
    
    def test_overview_no_sessions(self):
        """Test overview with no completed sessions."""
        new_user = User.objects.create_user(
            email='newuser@example.com',
            password='testpass123',
        )
        client = APIClient()
        client.force_authenticate(user=new_user)
        
        response = client.get('/api/analytics/overview')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_sessions'], 0)
        self.assertEqual(response.data['overall_score'], 0.0)


class AnalyticsSkillsTests(TestCase):
    """Test analytics skills endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        
        # Create role and session
        self.role = RoleCatalog.objects.create(
            name='Backend Engineer',
            category='backend',
            description='Backend development role',
            keywords_json=['python', 'django'],
            level_keywords_json={'junior': ['python'], 'mid': ['django'], 'senior': ['architecture']}
        )
        
        self.session = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='technical',
            status='completed',
            overall_score=70
        )
        
        # Create question and answer with skill tags
        question = InterviewQuestion.objects.create(
            session=self.session,
            order=1,
            question_text='What is Django?',
            category='technical',
            difficulty='medium',
            skill_tags_json=['backend.django.auth']
        )
        
        InterviewAnswer.objects.create(
            question=question,
            answer_text='Django is a web framework.',
            time_seconds=120,
            scores_json={
                'structure': 3,
                'relevance': 4,
                'technical_accuracy': 3,
                'depth': 2,
                'communication': 3,
            },
            feedback_json={
                'strengths': ['Clear'],
                'weaknesses': ['Needs depth'],
            },
            skill_tags_json=['backend.django.auth']
        )
    
    def test_get_skills(self):
        """Test getting skill analytics."""
        response = self.client.get('/api/analytics/skills')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('skills', response.data)
        self.assertIsInstance(response.data['skills'], list)
        
        # If skills exist, check structure
        if response.data['skills']:
            skill = response.data['skills'][0]
            self.assertIn('tag', skill)
            self.assertIn('rolling_score', skill)
            self.assertIn('attempts', skill)
            self.assertIn('last_practiced_at', skill)
            self.assertIn('trend', skill)


class AnalyticsSessionsTests(TestCase):
    """Test analytics sessions endpoint."""
    
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
        
        # Create sessions
        self.session1 = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='technical',
            status='completed',
            overall_score=70
        )
        
        self.session2 = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='hr',
            status='completed',
            overall_score=80
        )
    
    def test_get_sessions(self):
        """Test getting session history."""
        response = self.client.get('/api/analytics/sessions')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertGreaterEqual(response.data['count'], 2)
        
        # Check session structure
        if response.data['results']:
            session = response.data['results'][0]
            self.assertIn('id', session)
            self.assertIn('role', session)
            self.assertIn('type', session)
            self.assertIn('score', session)
            self.assertIn('date', session)
    
    def test_filter_sessions_by_type(self):
        """Test filtering sessions by type."""
        response = self.client.get('/api/analytics/sessions', {'type': 'technical'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        # All results should be technical type
        self.assertTrue(all(s['type'] == 'technical' for s in results))


class AnalyticsServiceTests(TestCase):
    """Test analytics service functions."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        
        self.role = RoleCatalog.objects.create(
            name='Backend Engineer',
            category='backend',
            description='Backend development role',
            keywords_json=['python', 'django'],
            level_keywords_json={'junior': ['python'], 'mid': ['django'], 'senior': ['architecture']}
        )
        
        self.session = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='technical',
            status='completed',
            overall_score=70
        )
    
    def test_get_session_stats(self):
        """Test getting session stats."""
        from analytics.services.aggregator import get_session_stats
        
        stats = get_session_stats(self.user)
        
        self.assertIn('total_sessions', stats)
        self.assertIn('completed_sessions', stats)
        self.assertIn('average_score', stats)
        self.assertGreaterEqual(stats['total_sessions'], 1)
    
    def test_calculate_score_trend(self):
        """Test calculating score trend."""
        from analytics.services.calculator import calculate_score_trend
        
        sessions = InterviewSession.objects.filter(user=self.user, status='completed')
        trend = calculate_score_trend(sessions)
        
        self.assertIsInstance(trend, list)
        if trend:
            self.assertIn('date', trend[0])
            self.assertIn('score', trend[0])
    
    def test_calculate_category_trend(self):
        """Test calculating category trend."""
        from analytics.services.calculator import calculate_category_trend
        
        sessions = InterviewSession.objects.filter(user=self.user, status='completed')
        trend = calculate_category_trend(sessions)
        
        self.assertIsInstance(trend, dict)
        self.assertIn('technical', trend)
        self.assertIn('hr', trend)
        self.assertIn('case', trend)
        self.assertIn('mixed', trend)
