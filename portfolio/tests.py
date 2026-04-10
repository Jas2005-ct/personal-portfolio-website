from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser, Profile, Skill, Project, ContactMessage

class PortfolioTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            name='Test User',
            title='Test Title',
            bio='Test Bio',
            address='Test Address',
            phone='1234567890',
            philosophy='Test Philosophy'
        )
        self.skill = Skill.objects.create(
            user=self.user,
            skill='Python',
            level='Advanced',
            category='Backend'
        )
        self.project = Project.objects.create(
            user=self.user,
            title='Test Project',
            description='Test Description',
            motive='Test Motive',
            problem_statement='Test Problem',
            impact='Increased test coverage by 100%',
            architecture_notes='Uses Django and REST Framework'
        )

    def test_portfolio_data_api(self):
        """Test the public API endpoint that gathers all portfolio data."""
        url = reverse('portfolio-data')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profile']['name'], 'Test User')
        self.assertEqual(response.data['profile']['philosophy'], 'Test Philosophy')
        self.assertEqual(len(response.data['skills']), 1)
        self.assertEqual(response.data['skills'][0]['category'], 'Backend')
        self.assertEqual(response.data['projects'][0]['impact'], 'Increased test coverage by 100%')

    def test_contact_message_submission(self):
        """Test anonymous submission of contact messages."""
        url = '/api/contact/'
        data = {
            'sender_name': 'Inquirer',
            'sender_email': 'inquirer@example.com',
            'subject': 'Inquiry',
            'message': 'Hello, I am interested in your work.'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.filter(sender_name='Inquirer').count(), 1)

    def test_protected_dashboard_access(self):
        """Test that the dashboard is protected from non-superusers."""
        url = reverse('dashboard')
        # Not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        
        # Logged in as regular user
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        
        # Logged in as superuser
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
