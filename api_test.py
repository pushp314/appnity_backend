#!/usr/bin/env python3
"""
API Testing Script for Appnity Backend

This script tests all major API endpoints to ensure they're working correctly.
Run this after setting up the backend to verify everything is functioning.

Usage:
    python api_test.py
"""

import requests
import json
import sys
from datetime import datetime


class APITester:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        
    def log(self, message, status='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        status_colors = {
            'INFO': '\033[94m',
            'SUCCESS': '\033[92m',
            'ERROR': '\033[91m',
            'WARNING': '\033[93m'
        }
        color = status_colors.get(status, '')
        reset = '\033[0m'
        print(f"{color}[{timestamp}] {status}: {message}{reset}")

    def test_endpoint(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                self.log(f"Unsupported method: {method}", 'ERROR')
                return False

            if response.status_code == expected_status:
                self.log(f"✅ {method} {endpoint} - Status: {response.status_code}", 'SUCCESS')
                return True
            else:
                self.log(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}", 'ERROR')
                if response.text:
                    self.log(f"Response: {response.text[:200]}...", 'ERROR')
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ {method} {endpoint} - Connection error: {e}", 'ERROR')
            return False

    def authenticate(self):
        """Authenticate and get access token"""
        self.log("🔐 Testing authentication...")
        
        # Test user registration (might fail if user exists)
        register_data = {
            "email": "test@appnity.co.in",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
            "password_confirm": "testpass123"
        }
        
        self.test_endpoint('POST', '/api/v1/auth/register/', register_data, expected_status=201)
        
        # Test login
        login_data = {
            "email": "test@appnity.co.in",
            "password": "testpass123"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/auth/login/", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('tokens', {}).get('access')
                self.log("✅ Authentication successful", 'SUCCESS')
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code}", 'ERROR')
                return False
        except Exception as e:
            self.log(f"❌ Authentication error: {e}", 'ERROR')
            return False

    def get_auth_headers(self):
        """Get authorization headers"""
        if self.access_token:
            return {'Authorization': f'Bearer {self.access_token}'}
        return {}

    def test_public_endpoints(self):
        """Test public API endpoints"""
        self.log("🌐 Testing public endpoints...")
        
        endpoints = [
            ('GET', '/api/v1/blogs/'),
            ('GET', '/api/v1/blogs/featured/'),
            ('GET', '/api/v1/blogs/recent/'),
            ('GET', '/api/v1/blogs/categories/'),
            ('GET', '/api/v1/blogs/tags/'),
            ('GET', '/api/v1/products/'),
            ('GET', '/api/v1/products/featured/'),
            ('GET', '/api/v1/portfolio/'),
            ('GET', '/api/v1/portfolio/featured/'),
            ('GET', '/api/v1/training/courses/'),
            ('GET', '/api/v1/training/courses/featured/'),
            ('GET', '/api/v1/training/instructors/'),
            ('GET', '/api/v1/careers/positions/'),
            ('GET', '/api/v1/careers/positions/open/'),
            ('GET', '/api/v1/testimonials/'),
            ('GET', '/api/v1/testimonials/featured/'),
        ]
        
        success_count = 0
        for method, endpoint in endpoints:
            if self.test_endpoint(method, endpoint):
                success_count += 1
        
        self.log(f"Public endpoints: {success_count}/{len(endpoints)} passed", 
                'SUCCESS' if success_count == len(endpoints) else 'WARNING')

    def test_contact_form(self):
        """Test contact form submission"""
        self.log("📧 Testing contact form...")
        
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "inquiry_type": "general",
            "message": "This is a test message from the API testing script."
        }
        
        return self.test_endpoint('POST', '/api/v1/contacts/', contact_data, expected_status=201)

    def test_newsletter(self):
        """Test newsletter subscription"""
        self.log("📰 Testing newsletter subscription...")
        
        newsletter_data = {
            "email": "newsletter-test@example.com"
        }
        
        return self.test_endpoint('POST', '/api/v1/newsletter/subscribe/', newsletter_data, expected_status=201)

    def test_testimonial_submission(self):
        """Test testimonial submission"""
        self.log("💬 Testing testimonial submission...")
        
        testimonial_data = {
            "name": "Test User",
            "email": "test@example.com",
            "title": "Developer",
            "company": "Test Company",
            "content": "This is a test testimonial for the API testing script.",
            "rating": 5,
            "product_name": "CodeGram"
        }
        
        return self.test_endpoint('POST', '/api/v1/testimonials/submit/', testimonial_data, expected_status=201)

    def test_authenticated_endpoints(self):
        """Test authenticated endpoints"""
        if not self.access_token:
            self.log("⚠️ Skipping authenticated tests - no access token", 'WARNING')
            return
            
        self.log("🔒 Testing authenticated endpoints...")
        
        headers = self.get_auth_headers()
        
        endpoints = [
            ('GET', '/api/v1/auth/profile/'),
            ('GET', '/api/v1/contacts/list/'),
            ('GET', '/api/v1/newsletter/list/'),
        ]
        
        success_count = 0
        for method, endpoint in endpoints:
            if self.test_endpoint(method, endpoint, headers=headers):
                success_count += 1
        
        self.log(f"Authenticated endpoints: {success_count}/{len(endpoints)} passed", 
                'SUCCESS' if success_count == len(endpoints) else 'WARNING')

    def test_api_documentation(self):
        """Test API documentation endpoints"""
        self.log("📚 Testing API documentation...")
        
        endpoints = [
            ('GET', '/api/schema/', 200),
            ('GET', '/api/docs/', 200),
            ('GET', '/api/redoc/', 200),
        ]
        
        success_count = 0
        for method, endpoint, expected_status in endpoints:
            if self.test_endpoint(method, endpoint, expected_status=expected_status):
                success_count += 1
        
        self.log(f"Documentation endpoints: {success_count}/{len(endpoints)} passed", 
                'SUCCESS' if success_count == len(endpoints) else 'WARNING')

    def run_all_tests(self):
        """Run all API tests"""
        self.log("🧪 Starting API tests for Appnity Backend...", 'INFO')
        self.log(f"Base URL: {self.base_url}", 'INFO')
        
        # Test server connectivity
        try:
            response = requests.get(f"{self.base_url}/api/v1/", timeout=10)
            self.log("✅ Server is reachable", 'SUCCESS')
        except requests.exceptions.RequestException:
            self.log("❌ Cannot reach server. Is it running?", 'ERROR')
            return False

        # Run tests
        tests = [
            self.test_public_endpoints,
            self.test_contact_form,
            self.test_newsletter,
            self.test_testimonial_submission,
            self.test_api_documentation,
            self.authenticate,
            self.test_authenticated_endpoints,
        ]
        
        passed_tests = 0
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                self.log(f"❌ Test failed with exception: {e}", 'ERROR')
        
        # Summary
        self.log("", 'INFO')
        self.log("=" * 50, 'INFO')
        self.log(f"API Test Summary: {passed_tests}/{len(tests)} test suites passed", 
                'SUCCESS' if passed_tests == len(tests) else 'WARNING')
        
        if passed_tests == len(tests):
            self.log("🎉 All tests passed! Your API is working correctly.", 'SUCCESS')
        else:
            self.log("⚠️ Some tests failed. Check the logs above for details.", 'WARNING')
        
        return passed_tests == len(tests)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Appnity Backend API')
    parser.add_argument(
        '--url', 
        default='http://localhost:8000',
        help='Base URL for the API (default: http://localhost:8000)'
    )
    
    args = parser.parse_args()
    
    tester = APITester(args.url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()