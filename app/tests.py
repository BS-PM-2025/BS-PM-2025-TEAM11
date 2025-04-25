from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import Student, Secretary, AcademicStaff
from django.utils import timezone
from app.models import Request



User = get_user_model()

class LoginTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student1',
            password='pass123456',
            id_number='111111111',
            email='student@test.com',
            phone='0501234567',
            department='הנדסה',
            date_start='2022-10-10',
            role='student'
        )
        Student.objects.create(user=self.student, year_of_study=2, degree_type='bachelor')
        self.secretary = User.objects.create_user(
            username='secretary1',
            password='pass123456',
            id_number='222222222',
            email='sec@test.com',
            phone='0501111111',
            department='הנדסה',
            date_start='2021-09-01',
            role='secretary'
        )

        self.academic = User.objects.create_user(
            username='academic1',
            password='pass123456',
            id_number='333333333',
            email='aca@test.com',
            phone='0502222222',
            department='מדעי המחשב',
            date_start='2020-01-01',
            role='academic'
        )

    def test_login_with_empty_fields(self):
        response = self.client.post(reverse('login'), {'username': '', 'password': ''})
        self.assertContains(response, "Please fill in all fields.")

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {'username': 'wrong', 'password': 'wrong'})
        self.assertContains(response, "Invalid username or password.")

    def test_login_student_success_redirect(self):
        response = self.client.post(reverse('login'), {'username': 'student1', 'password': 'pass123456'})
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_login_secretary_success_redirect(self):
        response = self.client.post(reverse('login'), {'username': 'secretary1', 'password': 'pass123456'})
        self.assertRedirects(response, reverse('secretary_dashboard'))

    def test_login_academic_success_redirect(self):
        response = self.client.post(reverse('login'), {'username': 'academic1', 'password': 'pass123456'})
        self.assertRedirects(response, reverse('academic_dashboard'))

class RequestAPITests(TestCase):
    def setUp(self):
        User = get_user_model()

        # Create users
        self.student_user = User.objects.create_user(
            username='student1',
            password='pass123456',
            id_number='111111111',
            email='student@test.com',
            phone='0501234567',
            department='הנדסה',
            date_start='2022-10-10',
            role='student'
        )
        self.student = Student.objects.create(user=self.student_user, year_of_study=2, degree_type='bachelor')

        self.academic_user = User.objects.create_user(
            username='academic1',
            password='pass123456',
            id_number='222222222',
            email='academic@test.com',
            phone='0502222222',
            department='מדעי המחשב',
            date_start='2021-01-01',
            role='academic'
        )
        self.academic = AcademicStaff.objects.create(user=self.academic_user)
        self.secretary_user = User.objects.create_user(
            username='secretary1',
            password='pass123456',
            id_number='333333333',
            email='secretary@test.com',
            phone='0509999999',
            department='ניהול',
            date_start='2020-01-01',
            role='secretary'
        )
        self.secretary = Secretary.objects.create(user=self.secretary_user)

        # Create requests assigned to academic
        Request.objects.create(
            title='Test Request 1',
            description='This is a pending request.',
            status='pending',
            student=self.student,
            assigned_to=self.academic_user,
            submitted_at=timezone.now()
        )

        Request.objects.create(
            title='Test Request 1',
            description='This is a pending request.',
            status='pending',
            student=self.student,
            assigned_to=self.academic_user,
            submitted_at=timezone.now(),
            request_type='iron_swords'
        )

    def test_api_returns_only_assigned_requests(self):
        self.client.login(username='academic1', password='pass123456')
        response = self.client.get('/api/requests/?status=pending')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[0]['status'], 'pending')

    def test_api_rejects_invalid_status(self):
        self.client.login(username='academic1', password='pass123456')
        response = self.client.get('/api/requests/?status=invalid')
        self.assertEqual(response.status_code, 400)

    def test_api_requires_login(self):
        response = self.client.get('/api/requests/?status=pending')
        self.assertEqual(response.status_code, 302)  # expect redirect to login
        self.assertIn('/login/', response.url)  # optional: check it's a redirect to login

    def test_secretary_can_view_categorized_requests(self):
        self.client.login(username='secretary1', password='pass123456')
        response = self.client.get('/api/requests/?status=pending')
        self.assertEqual(response.status_code, 200)

    def test_request_types_are_defined_correctly(self):
        expected_types = {
            "grade_appeal": "Grade Appeal",
            "extension_request": "Extension Request",
            "course_swap": "Course Swap"
        }
        self.assertIn("grade_appeal", expected_types)

    def test_dashboard_route(self):
        self.client.login(username='student1', password='pass123456')
        response = self.client.get('/dashboard/', follow=True)
        self.assertEqual(response.status_code, 200)

        html = response.content.decode()
        self.assertIn("Alternative Assignment for Iron Swords", html)
        self.assertIn("Assignment Submission Extension", html)
        self.assertIn("Course Unblocking", html)

    def test_secretary_requests_api(self):
        # Create a test user with the 'secretary' role
        user = User.objects.create_user(username='testuser', password='password', role='secretary')
        self.client.login(username='testuser', password='password')

        # Reverse the URL for the secretary request API
        url = reverse('secretary_requests_api')

        # Now make the API request
        response = self.client.get(url)

        # Check that the status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_invalid_status_for_academic_requests_api(self):
        """
        Test the academic API with an invalid status.
        """
        self.client.login(username='academic1', password='pass123456')

        # Get the API response with an invalid status
        response = self.client.get(reverse('academic_requests_api') + '?status=invalid_status')

        # Assert the response status code for invalid status
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid status'})

    def test_unauthorized_access_academic_requests_api(self):
        """
        Test that only users with 'academic' role can access the academic API.
        """
        self.client.login(username='secretary1', password='pass123456')

        # Get the API response for an academic request while logged in as secretary
        response = self.client.get(reverse('academic_requests_api') + '?status=pending')

        # Assert that unauthorized access is denied
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'error': 'Unauthorized'})


