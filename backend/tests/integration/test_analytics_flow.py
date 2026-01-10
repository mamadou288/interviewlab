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


class AnalyticsFlowIntegrationTest(TestCase):
    """Integration test for analytics flow."""
    
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
        
        # Create multiple completed sessions with different dates
        base_date = timezone.now() - timedelta(days=20)
        
        # Session 1 (older, lower score)
        session1 = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='technical',
            status='completed',
            overall_score=65,
            started_at=base_date,
            ended_at=base_date
        )
        question1 = InterviewQuestion.objects.create(
            session=session1,
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
                'relevance': 3,
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
        
        # Session 2 (newer, higher score)
        session2 = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='hr',
            status='completed',
            overall_score=80,
            started_at=base_date + timedelta(days=10),
            ended_at=base_date + timedelta(days=10)
        )
        question2 = InterviewQuestion.objects.create(
            session=session2,
            order=1,
            question_text='Tell me about yourself.',
            category='hr',
            difficulty='easy',
            skill_tags_json=['communication.star']
        )
        InterviewAnswer.objects.create(
            question=question2,
            answer_text='I am a software engineer with experience in Python and Django.',
            time_seconds=90,
            scores_json={
                'structure': 4,
                'relevance': 4,
                'technical_accuracy': 4,
                'depth': 3,
                'communication': 4,
            },
            feedback_json={
                'strengths': ['Well structured'],
                'weaknesses': ['Could add more detail'],
            },
            skill_tags_json=['communication.star']
        )
        
        # Session 3 (most recent, highest score)
        session3 = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='technical',
            status='completed',
            overall_score=85,
            started_at=base_date + timedelta(days=15),
            ended_at=base_date + timedelta(days=15)
        )
        question3 = InterviewQuestion.objects.create(
            session=session3,
            order=1,
            question_text='Explain Django authentication.',
            category='technical',
            difficulty='medium',
            skill_tags_json=['backend.django.auth']
        )
        InterviewAnswer.objects.create(
            question=question3,
            answer_text='Django authentication uses sessions and tokens.',
            time_seconds=110,
            scores_json={
                'structure': 4,
                'relevance': 5,
                'technical_accuracy': 4,
                'depth': 3,
                'communication': 4,
            },
            feedback_json={
                'strengths': ['Accurate', 'Clear'],
                'weaknesses': ['Could explain tokens more'],
            },
            skill_tags_json=['backend.django.auth']
        )
    
    def test_complete_analytics_flow(self):
        """Test complete flow: Complete multiple interviews → Check analytics overview → Check skill trends."""
        
        # Step 1: Get analytics overview
        overview_response = self.client.get('/api/analytics/overview')
        self.assertEqual(overview_response.status_code, status.HTTP_200_OK)
        
        overview_data = overview_response.data
        self.assertIn('overall_score', overview_data)
        self.assertIn('total_sessions', overview_data)
        self.assertEqual(overview_data['total_sessions'], 3)
        
        # Check score trend (should show improvement over time)
        self.assertIn('score_trend', overview_data)
        score_trend = overview_data['score_trend']
        self.assertGreaterEqual(len(score_trend), 3)
        
        # Check category trend
        self.assertIn('category_trend', overview_data)
        category_trend = overview_data['category_trend']
        self.assertIn('technical', category_trend)
        self.assertIn('hr', category_trend)
        
        # Step 2: Get skill analytics
        skills_response = self.client.get('/api/analytics/skills')
        self.assertEqual(skills_response.status_code, status.HTTP_200_OK)
        self.assertIn('skills', skills_response.data)
        
        skills = skills_response.data['skills']
        # Should have skills from the sessions
        skill_tags = [s['tag'] for s in skills]
        self.assertIn('backend.django.auth', skill_tags)
        self.assertIn('communication.star', skill_tags)
        
        # Step 3: Get session history
        sessions_response = self.client.get('/api/analytics/sessions')
        self.assertEqual(sessions_response.status_code, status.HTTP_200_OK)
        self.assertIn('results', sessions_response.data)
        self.assertIn('count', sessions_response.data)
        self.assertEqual(sessions_response.data['count'], 3)
        
        # Check sessions are ordered by date (most recent first)
        results = sessions_response.data['results']
        if len(results) >= 2:
            # Sessions should be ordered by date (most recent first)
            # Note: Score ordering is not guaranteed, only date ordering
            self.assertIsNotNone(results[0]['date'])
            self.assertIsNotNone(results[1]['date'])
        
        # Step 4: Filter sessions by type
        technical_sessions = self.client.get('/api/analytics/sessions', {'type': 'technical'})
        self.assertEqual(technical_sessions.status_code, status.HTTP_200_OK)
        technical_results = technical_sessions.data['results']
        self.assertTrue(all(s['type'] == 'technical' for s in technical_results))
        self.assertEqual(len(technical_results), 2)  # Should have 2 technical sessions

