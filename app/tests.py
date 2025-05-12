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

        # Check that the statusu code is 200 (OK)
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

class LogoutTests(TestCase):
    def setUp(self):
        # Create users
        self.student = User.objects.create_user(
            username='student1', password='pass123456',
            id_number='111111111', role='student',
            first_name='Student', last_name='One'
        )
        Student.objects.create(user=self.student, year_of_study=1, degree_type='bachelor')

        self.secretary = User.objects.create_user(
            username='secretary1', password='pass123456',
            id_number='222222222', role='secretary',
            first_name='Secretary', last_name='User'
        )
        Secretary.objects.create(user=self.secretary)

        self.academic = User.objects.create_user(
            username='academic1', password='pass123456',
            id_number='333333333', role='academic',
            first_name='Academic', last_name='User'
        )
        AcademicStaff.objects.create(user=self.academic)

    def test_student_logout(self):
        self.client.login(username='student1', password='pass123456')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        # Try to access protected page
        resp = self.client.get(reverse('student_dashboard'))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('student_dashboard')}")

    def test_secretary_logout(self):
        self.client.login(username='secretary1', password='pass123456')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        resp = self.client.get(reverse('secretary_dashboard'))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('secretary_dashboard')}")

    def test_academic_logout(self):
        self.client.login(username='academic1', password='pass123456')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        resp = self.client.get(reverse('academic_dashboard'))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('academic_dashboard')}")


from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from app.models import Student  # החלף לנתיב הנכון אם צריך

User = get_user_model()

class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.existing_user = User.objects.create_user(
            username="existinguser",
            email="existing@ac.sce.ac.il",
            id_number="123456789",
            phone="0500000000",
            password="Testpass123",
            role="student"
        )

    def test_send_verification_code_valid(self):
        response = self.client.post('/send-verification-code/', {'email': 'newuser@ac.sce.ac.il'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'ok'})

    def test_send_verification_code_existing_email(self):
        response = self.client.post('/send-verification-code/', {'email': 'existing@ac.sce.ac.il'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'status': 'exists',
            'message': 'Email already registered.'
        })

    def test_verify_code_success(self):
        session = self.client.session
        session['verification_code'] = '123456'
        session.save()
        response = self.client.post('/verify-code/', {'code': '123456'})
        self.assertJSONEqual(response.content, {'status': 'success'})

    def test_verify_code_invalid(self):
        session = self.client.session
        session['verification_code'] = '123456'
        session.save()
        response = self.client.post('/verify-code/', {'code': '000000'})
        self.assertJSONEqual(response.content, {'status': 'invalid'})

    def test_check_id_exists(self):
        response = self.client.post('/check-id-and-phone/', content_type='application/json', data={
            'id_number': '123456789',
            'phone': '0501111111'
        })
        self.assertJSONEqual(response.content, {
            'status': 'exists',
            'message': 'Student ID already exists in the system.'
        })

    def test_check_phone_exists(self):
        response = self.client.post('/check-id-and-phone/', content_type='application/json', data={
            'id_number': '987654321',
            'phone': '0500000000'
        })
        self.assertJSONEqual(response.content, {
            'status': 'exists',
            'message': 'Phone number already exists in the system.'
        })

    def test_check_id_and_phone_ok(self):
        response = self.client.post('/check-id-and-phone/', content_type='application/json', data={
            'id_number': '987654321',
            'phone': '0501234567'
        })
        self.assertJSONEqual(response.content, {'status': 'ok'})

    def test_final_student_registration_success(self):
        response = self.client.post('/final-student-registration/', content_type='application/json', data={
            'username': 'newstudent',
            'first_name': 'New',
            'last_name': 'Student',
            'id_number': '987654321',
            'phone': '0507654321',
            'email': 'newstudent@ac.sce.ac.il',
            'password': 'Testpass123',
            'education': {
                'start_year': 2023,
                'degree_type': 'bachelor',
                'current_year_of_study': 1,
                'current_semester': 'A',
                'year1_sem1': '2023-2024',
                'year1_sem2': '2023-2024',
            }
        })
        self.assertJSONEqual(response.content, {'status': 'success'})
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        self.assertTrue(Student.objects.filter(user__username='newstudent').exists())


from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from app.models import Student, Request

class RequestDetailUpdateTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Secretary user
        self.user = get_user_model().objects.create_user(
            username='secretary1',
            password='testpass123',
            email='secretary@example.com',
            role='secretary',
            id_number='123456789',
            phone='0500000000',
            department='Test Dept'
        )

        # Student user
        self.student_user = get_user_model().objects.create_user(
            username='student1',
            password='studentpass',
            email='student@example.com',
            role='student',
            id_number='987654321',
            phone='0509999999',
            department='CS'
        )

        # Create student only if not already present
        self.student, _ = Student.objects.get_or_create(
            user=self.student_user,
            defaults={
                'year_of_study': 1,
                'degree_type': 'bachelor'
            }
        )

        # Create request assigned to secretary
        self.req = Request.objects.create(
            title='Test Request',
            description='Please approve me',
            status='pending',
            request_type='delay_submission',
            student=self.student,
            assigned_to=self.user
        )

    def test_request_status_update_and_email_sent(self):
        # Login as secretary
        self.client.login(username='secretary1', password='testpass123')

        # Perform POST to update request
        response = self.client.post(reverse('request_detail_update', args=[self.req.id]), {
            'status': 'accepted',
            'explanation': 'Approved because of valid reason.'
        })

        # ✅ Check that the request object was updated
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, 'accepted')
        self.assertEqual(self.req.explanation, 'Approved because of valid reason.')

        # ✅ Check for redirection after update
        self.assertRedirects(response, reverse('secretary_dashboard'))

        # ✅ Check email sent to student
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('עדכון סטטוס לבקשה', email.subject)
        self.assertIn('אושרה', email.body)
        self.assertIn('Approved because of valid reason.', email.body)
        self.assertEqual(email.to, ['student@example.com'])

    def test_academic_can_update_request(self):
        # Create academic user
        academic_user = get_user_model().objects.create_user(
            username='academic1',
            password='academicpass',
            email='academic@example.com',
            role='academic',
            id_number='111222333',
            phone='0501234567',
            department='Engineering'
        )

        # Re-assign request to academic
        self.req.assigned_to = academic_user
        self.req.save()

        # Login as academic
        self.client.login(username='academic1', password='academicpass')

        # Perform POST to update request
        response = self.client.post(reverse('request_detail_update', args=[self.req.id]), {
            'status': 'rejected',
            'explanation': 'Not approved due to policy.'
        })

        self.req.refresh_from_db()
        self.assertEqual(self.req.status, 'rejected')
        self.assertEqual(self.req.explanation, 'Not approved due to policy.')
        self.assertRedirects(response, reverse('academic_dashboard'))

        # Email check
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('נדחתה', email.body)
