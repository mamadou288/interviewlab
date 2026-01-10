from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from interviews.models import InterviewSession, InterviewQuestion, InterviewAnswer
from roles.models import RoleCatalog
from profiles.models import Profile
from .models import UpgradePlan, PlanTemplate

User = get_user_model()


class UpgradePlanTests(TestCase):
    """Test upgrade plan generation."""
    
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
        
        # Create completed session
        self.session = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='technical',
            status='completed',
            overall_score=65
        )
        
        # Create question and answer
        self.question = InterviewQuestion.objects.create(
            session=self.session,
            order=1,
            question_text='What is Django?',
            category='technical',
            difficulty='medium',
            skill_tags_json=['backend.django.auth']
        )
        
        self.answer = InterviewAnswer.objects.create(
            question=self.question,
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
                'weaknesses': ['Needs more depth'],
            },
            skill_tags_json=['backend.django.auth']
        )
    
    def test_generate_upgrade_plan(self):
        """Test generating an upgrade plan."""
        url = f'/api/interviews/{self.session.id}/upgrade-plan'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        # The serializer flattens plan_json fields, so check for them directly
        self.assertIn('strengths', response.data)
        self.assertIn('weaknesses', response.data)
        self.assertIn('learning_objectives', response.data)
        self.assertIn('daily_plans', response.data)
        self.assertIn('next_interview', response.data)
    
    def test_generate_upgrade_plan_with_duration(self):
        """Test generating upgrade plan with custom duration."""
        url = f'/api/interviews/{self.session.id}/upgrade-plan?duration_days=14'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['duration_days'], 14)
    
    def test_generate_upgrade_plan_invalid_duration(self):
        """Test generating upgrade plan with invalid duration."""
        url = f'/api/interviews/{self.session.id}/upgrade-plan?duration_days=30'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_generate_upgrade_plan_incomplete_session(self):
        """Test generating upgrade plan for incomplete session fails."""
        incomplete_session = InterviewSession.objects.create(
            user=self.user,
            role_selected=self.role,
            level='mid',
            type='technical',
            status='in_progress'
        )
        
        url = f'/api/interviews/{incomplete_session.id}/upgrade-plan'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PlanGeneratorServiceTests(TestCase):
    """Test plan generator service."""
    
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
            overall_score=65
        )
    
    def test_identify_skill_gaps(self):
        """Test identifying skill gaps."""
        from .services.generator import identify_skill_gaps
        
        skill_gaps = identify_skill_gaps(self.user, self.role, self.session)
        
        self.assertIsInstance(skill_gaps, list)
        # Should return list of skill tags
    
    def test_generate_upgrade_plan_service(self):
        """Test upgrade plan generation service."""
        from .services.generator import generate_upgrade_plan
        
        upgrade_plan = generate_upgrade_plan(str(self.session.id), duration_days=7)
        
        self.assertIsInstance(upgrade_plan, UpgradePlan)
        self.assertEqual(upgrade_plan.session, self.session)
        self.assertEqual(upgrade_plan.duration_days, 7)
        self.assertIn('strengths', upgrade_plan.plan_json)
        self.assertIn('weaknesses', upgrade_plan.plan_json)
        self.assertIn('daily_plans', upgrade_plan.plan_json)


class PlanTemplateTests(TestCase):
    """Test plan template model."""
    
    def test_create_plan_template(self):
        """Test creating a plan template."""
        template = PlanTemplate.objects.create(
            skill_tag='communication.star',
            title='STAR Method Mastery',
            description='Learn the STAR method',
            steps_json=[
                {
                    'day': 1,
                    'topic': 'STAR Introduction',
                    'drills': ['Read guide'],
                    'mini_mock': 'Tell me about a time...',
                    'quick_test': 'Answer 1 question'
                }
            ],
            difficulty='beginner',
            duration_minutes=45
        )
        
        self.assertEqual(template.skill_tag, 'communication.star')
        self.assertEqual(template.difficulty, 'beginner')
        self.assertIsInstance(template.steps_json, list)
