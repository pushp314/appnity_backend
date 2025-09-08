from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import PortfolioProject, ProjectTechnology, ProjectChallenge, ProjectResult

User = get_user_model()


class PortfolioProjectModelTest(TestCase):
    """Test PortfolioProject model"""

    def setUp(self):
        self.project = PortfolioProject.objects.create(
            title='Test Project',
            subtitle='Test Subtitle',
            description='# Test Description\n\nThis is a test project.',
            category='web',
            status='completed',
            duration='3 months',
            duration_weeks=12,
            team_size=3
        )

    def test_project_creation(self):
        """Test project creation and string representation"""
        self.assertEqual(str(self.project), 'Test Project')
        self.assertEqual(self.project.slug, 'test-project')
        self.assertTrue(self.project.description_html)

    def test_slug_generation(self):
        """Test automatic slug generation"""
        project = PortfolioProject.objects.create(
            title='Another Test Project',
            subtitle='Test',
            description='Test',
            category='web'
        )
        self.assertEqual(project.slug, 'another-test-project')


class PortfolioAPITest(APITestCase):
    """Test Portfolio API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            role='admin'
        )
        
        self.project = PortfolioProject.objects.create(
            title='API Test Project',
            subtitle='Test Subtitle',
            description='Test description',
            category='web',
            status='completed',
            duration='2 months',
            team_size=2,
            is_featured=True
        )
        
        # Add technologies
        ProjectTechnology.objects.create(
            project=self.project,
            name='React',
            category='Frontend',
            order=1
        )

    def test_portfolio_list_public_access(self):
        """Test public access to portfolio list"""
        url = reverse('portfolio-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_portfolio_detail_public_access(self):
        """Test public access to portfolio detail"""
        url = reverse('portfolio-detail', kwargs={'slug': self.project.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Test Project')

    def test_featured_projects(self):
        """Test featured projects endpoint"""
        url = reverse('featured-projects')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_projects_by_category(self):
        """Test projects by category endpoint"""
        url = reverse('projects-by-category', kwargs={'category': 'web'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_project_technologies(self):
        """Test project technologies endpoint"""
        url = reverse('project-technologies')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Frontend', response.data)

    def test_search_projects(self):
        """Test project search functionality"""
        url = reverse('search-projects')
        response = self.client.get(url, {'q': 'API Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_portfolio_create_requires_auth(self):
        """Test that creating projects requires authentication"""
        url = reverse('portfolio-list')
        data = {
            'title': 'New Project',
            'subtitle': 'Test',
            'description': 'Test description',
            'category': 'web'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_portfolio_create_with_auth(self):
        """Test creating project with admin authentication"""
        self.client.force_authenticate(user=self.user)
        url = reverse('portfolio-list')
        data = {
            'title': 'New Authenticated Project',
            'subtitle': 'Test Subtitle',
            'description': 'Test description',
            'category': 'web',
            'status': 'completed',
            'duration': '1 month',
            'team_size': 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_portfolio_stats_requires_admin(self):
        """Test that portfolio stats require admin access"""
        url = reverse('portfolio-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_portfolio_stats_with_admin(self):
        """Test portfolio stats with admin authentication"""
        self.client.force_authenticate(user=self.user)
        url = reverse('portfolio-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_projects', response.data)


class ProjectTechnologyTest(TestCase):
    """Test ProjectTechnology model"""

    def setUp(self):
        self.project = PortfolioProject.objects.create(
            title='Tech Test Project',
            subtitle='Test',
            description='Test',
            category='web'
        )

    def test_technology_creation(self):
        """Test technology creation"""
        tech = ProjectTechnology.objects.create(
            project=self.project,
            name='Django',
            category='Backend',
            order=1
        )
        self.assertEqual(str(tech), 'Tech Test Project - Django')


class ProjectChallengeTest(TestCase):
    """Test ProjectChallenge model"""

    def setUp(self):
        self.project = PortfolioProject.objects.create(
            title='Challenge Test Project',
            subtitle='Test',
            description='Test',
            category='web'
        )

    def test_challenge_creation(self):
        """Test challenge creation"""
        challenge = ProjectChallenge.objects.create(
            project=self.project,
            title='Test Challenge',
            description='This is a test challenge',
            solution='This is the solution',
            order=1
        )
        self.assertEqual(str(challenge), 'Challenge Test Project - Test Challenge')


class ProjectResultTest(TestCase):
    """Test ProjectResult model"""

    def setUp(self):
        self.project = PortfolioProject.objects.create(
            title='Result Test Project',
            subtitle='Test',
            description='Test',
            category='web'
        )

    def test_result_creation(self):
        """Test result creation"""
        result = ProjectResult.objects.create(
            project=self.project,
            title='Test Result',
            description='This is a test result',
            metric='100% success',
            order=1
        )
        self.assertEqual(str(result), 'Result Test Project - Test Result')