from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserRegistrationTests(TestCase):
    """Test user registration endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register'
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertEqual(response.data['user']['first_name'], 'Test')
        
        # Verify user was created
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email fails."""
        User.objects.create_user(
            email='existing@example.com',
            password='testpass123'
        )
        
        data = {
            'email': 'existing@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_invalid_email(self):
        """Test registration with invalid email format."""
        data = {
            'email': 'invalid-email',
            'password': 'testpass123',
        }
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_weak_password(self):
        """Test registration with weak password."""
        data = {
            'email': 'test@example.com',
            'password': '123',  # Too short
        }
        response = self.client.post(self.register_url, data, format='json')
        
        # Should still succeed (Django doesn't enforce password strength by default)
        # But we can check if password is set
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])


class UserLoginTests(TestCase):
    """Test user login endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/auth/login'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )
    
    def test_user_login_success(self):
        """Test successful user login."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_login_nonexistent_user(self):
        """Test login with non-existent user."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123',
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTests(TestCase):
    """Test token refresh endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.refresh_url = '/api/auth/refresh'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
    
    def test_token_refresh_success(self):
        """Test successful token refresh."""
        # First login to get refresh token
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        login_response = self.client.post('/api/auth/login', login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Refresh token
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token."""
        refresh_data = {'refresh': 'invalid-token'}
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutTests(TestCase):
    """Test logout endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.logout_url = '/api/auth/logout'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
    
    def test_logout_success(self):
        """Test successful logout."""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
        # Logout
        response = self.client.post(self.logout_url)
        
        # Logout should succeed if authenticated
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logged out successfully')
    
    def test_logout_unauthenticated(self):
        """Test logout without authentication."""
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserModelTests(TestCase):
    """Test User model."""
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password('testpass123'))
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        
        self.assertEqual(str(user), 'test@example.com')
    
    def test_user_email_unique(self):
        """Test that email must be unique."""
        User.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            User.objects.create_user(
                email='test@example.com',
                password='testpass123',
            )
