from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import RoleCatalog, RoleSuggestion
from profiles.models import CVDocument, Profile

User = get_user_model()


class RoleListTests(TestCase):
    """Test role list endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        self.roles_url = '/api/roles'
        
        # Create test roles
        self.role1 = RoleCatalog.objects.create(
            name='Backend Engineer',
            category='backend',
            description='Backend development role',
            keywords_json=['python', 'django', 'postgresql'],
            level_keywords_json={'junior': ['python'], 'mid': ['django'], 'senior': ['architecture']}
        )
        self.role2 = RoleCatalog.objects.create(
            name='Frontend Developer',
            category='frontend',
            description='Frontend development role',
            keywords_json=['javascript', 'react', 'css'],
            level_keywords_json={'junior': ['javascript'], 'mid': ['react'], 'senior': ['typescript']}
        )
    
    def test_list_roles(self):
        """Test listing all roles."""
        response = self.client.get(self.roles_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_search_roles(self):
        """Test searching roles."""
        response = self.client.get(self.roles_url, {'search': 'backend'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        # Should find backend-related roles
        self.assertTrue(any('backend' in r['name'].lower() or 'backend' in r['category'].lower() 
                          for r in results))
    
    def test_filter_roles_by_category(self):
        """Test filtering roles by category."""
        response = self.client.get(self.roles_url, {'category': 'backend'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        # All results should be backend category
        self.assertTrue(all(r['category'] == 'backend' for r in results))


class RoleSuggestionsTests(TestCase):
    """Test role suggestions endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test roles
        self.backend_role = RoleCatalog.objects.create(
            name='Backend Engineer',
            category='backend',
            description='Backend development role',
            keywords_json=['python', 'django', 'postgresql', 'api'],
            level_keywords_json={'junior': ['python'], 'mid': ['django'], 'senior': ['architecture']}
        )
        self.frontend_role = RoleCatalog.objects.create(
            name='Frontend Developer',
            category='frontend',
            description='Frontend development role',
            keywords_json=['javascript', 'react', 'css'],
            level_keywords_json={'junior': ['javascript'], 'mid': ['react'], 'senior': ['typescript']}
        )
        
        # Create CV document and profile
        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile(
            "test_cv.pdf",
            b"Python Django PostgreSQL API",
            content_type="application/pdf"
        )
        self.cv_doc = CVDocument.objects.create(
            user=self.user,
            file=file,
            status='completed',
            file_size=len(b"Python Django PostgreSQL API"),
            mime_type='application/pdf',
            extracted_text='Python Django PostgreSQL API'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            cv_document=self.cv_doc,
            data_json={
                'skills': ['Python', 'Django', 'PostgreSQL'],
                'experience': [
                    {
                        'title': 'Backend Developer',
                        'company': 'Tech Corp',
                        'description': 'Worked with Python and Django'
                    }
                ]
            }
        )
    
    def test_get_role_suggestions(self):
        """Test getting role suggestions for a CV."""
        url = f'/api/cv/{self.cv_doc.id}/role-suggestions'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('suggestions', response.data)
        suggestions = response.data['suggestions']
        
        # Should have suggestions
        self.assertGreater(len(suggestions), 0)
        
        # Backend role should be suggested (higher score due to keyword matches)
        backend_suggestions = [s for s in suggestions if s['role']['name'] == 'Backend Engineer']
        self.assertGreater(len(backend_suggestions), 0)
        
        # Check suggestion structure
        suggestion = suggestions[0]
        self.assertIn('role', suggestion)
        self.assertIn('score', suggestion)
        self.assertIn('reasons_json', suggestion)
        # Score is DecimalField which serializes as string
        score_value = float(suggestion['score']) if isinstance(suggestion['score'], str) else suggestion['score']
        self.assertGreaterEqual(score_value, 0.0)
        self.assertLessEqual(score_value, 1.0)
    
    def test_role_suggestions_nonexistent_cv(self):
        """Test getting suggestions for non-existent CV."""
        import uuid
        fake_id = uuid.uuid4()
        url = f'/api/cv/{fake_id}/role-suggestions'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_role_suggestions_other_user_cv(self):
        """Test getting suggestions for another user's CV fails."""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
        )
        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile(
            "other_cv.pdf",
            b"Content",
            content_type="application/pdf"
        )
        other_cv = CVDocument.objects.create(
            user=other_user,
            file=file,
            status='completed',
            file_size=7,
            mime_type='application/pdf'
        )
        
        url = f'/api/cv/{other_cv.id}/role-suggestions'
        response = self.client.get(url)
        
        # Should return 403 (forbidden) - correct behavior for permission denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RoleSuggestionServiceTests(TestCase):
    """Test role suggestion service logic."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        
        # Create role
        self.role = RoleCatalog.objects.create(
            name='Backend Engineer',
            category='backend',
            description='Backend development role',
            keywords_json=['python', 'django', 'postgresql'],
            level_keywords_json={'junior': ['python'], 'mid': ['django'], 'senior': ['architecture']}
        )
        
        # Create profile with matching skills
        self.profile = Profile.objects.create(
            user=self.user,
            data_json={
                'skills': ['Python', 'Django', 'PostgreSQL'],
                'experience': [
                    {
                        'title': 'Backend Developer',
                        'company': 'Tech Corp'
                    }
                ]
            }
        )
    
    def test_suggestion_algorithm(self):
        """Test that suggestion algorithm calculates scores correctly."""
        from .services.suggester import suggest_roles
        from profiles.models import CVDocument
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create CV document
        file = SimpleUploadedFile(
            "test_cv.pdf",
            b"Python Django PostgreSQL",
            content_type="application/pdf"
        )
        cv_doc = CVDocument.objects.create(
            user=self.user,
            file=file,
            status='completed',
            file_size=len(b"Python Django PostgreSQL"),
            mime_type='application/pdf',
            extracted_text='Python Django PostgreSQL'
        )
        self.profile.cv_document = cv_doc
        self.profile.save()
        
        # Generate suggestions
        suggestions = suggest_roles(str(cv_doc.id))
        
        # Should generate suggestions
        self.assertGreater(len(suggestions), 0)
        
        # Check that backend role is suggested
        backend_suggestions = [s for s in suggestions if s.role.name == 'Backend Engineer']
        self.assertGreater(len(backend_suggestions), 0)
        
        # Check score is valid
        suggestion = backend_suggestions[0]
        self.assertGreaterEqual(suggestion.score, 0.0)
        self.assertLessEqual(suggestion.score, 1.0)
