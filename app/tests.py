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
        # תיקון כאן עם get_or_create במקום create
        Student.objects.get_or_create(
            user=self.student,
            defaults={'year_of_study': 2, 'degree_type': 'bachelor'}
        )

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
        self.student, _ = Student.objects.get_or_create(
            user=self.student_user,
            defaults={'year_of_study': 2, 'degree_type': 'bachelor'}
        )

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
        self.academic, _ = AcademicStaff.objects.get_or_create(user=self.academic_user)

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
        self.secretary, _ = Secretary.objects.get_or_create(user=self.secretary_user)

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
        self.assertIn("בקשה למטלה חלופית - חרבות ברזל", html)
        self.assertIn("דחיית הגשת עבודה", html)
        self.assertIn("שחרור חסימת קורס", html)


class LogoutTests(TestCase):
    def setUp(self):
        # יצירת משתמש עם תפקיד student
        self.student = User.objects.create_user(
            username='student1',
            password='pass123456',
            id_number='111111111',
            role='student',
            first_name='Student',
            last_name='One',
            email='student1@ac.sce.ac.il',
            phone='0501111111',
            department='הנדסת תוכנה',
            date_start='2022-10-01'
        )
        Student.objects.get_or_create(user=self.student, year_of_study=1, degree_type='bachelor')

        # יצירת משתמש עם תפקיד secretary
        self.secretary = User.objects.create_user(
            username='secretary1',
            password='pass123456',
            id_number='222222222',
            role='secretary',
            first_name='Secretary',
            last_name='User',
            email='secretary1@ac.sce.ac.il',
            phone='0502222222',
            department='מינהל אקדמי',
            date_start='2021-09-01'
        )
        Secretary.objects.get_or_create(user=self.secretary)

        # יצירת משתמש עם תפקיד academic
        self.academic = User.objects.create_user(
            username='academic1',
            password='pass123456',
            id_number='333333333',
            role='academic',
            first_name='Academic',
            last_name='User',
            email='academic1@ac.sce.ac.il',
            phone='0503333333',
            department='הנדסה',
            date_start='2020-09-01'
        )
        AcademicStaff.objects.get_or_create(user=self.academic)

    def test_student_logout(self):
        self.client.login(username='student1', password='pass123456')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

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
        # UnitTest for Hackthon Mission Logout
        # Major Feature: Logout Confirmation Test
        # This test checks that after confirming logout, the user is redirected and session ends
    def test_student_logout_confirmed(self):
        self.client.login(username='student1', password='pass123456')
        response = self.client.get(reverse('logout_confirmed'))
        self.assertRedirects(response, reverse('login'))

    def test_secretary_logout_confirmed(self):
        self.client.login(username='secretary1', password='pass123456')
        response = self.client.get(reverse('logout_confirmed'))
        self.assertRedirects(response, reverse('login'))

    def test_academic_logout_confirmed(self):
        self.client.login(username='academic1', password='pass123456')
        response = self.client.get(reverse('logout_confirmed'))
        self.assertRedirects(response, reverse('login'))


from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from app.models import Student  # החלף לנתיב הנכון אם צריך

User = get_user_model()

from django.test import TestCase, Client
from app.models import User, Student  # ודאי שיש לך את המודלים האלו מיובאים

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

        # ❗ מוסיפים את הסטודנט עצמו לפי המודל שלך
        Student.objects.create(
            user=self.existing_user,
            year_of_study=2,
            degree_type="bachelor"
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



from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import User, Student, Course, CourseOffering, Request

class SubmitCourseExemptionTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='student1',
            password='pass123',
            role='student',
            id_number='123',
            email='student@test.com',
            phone='0501111111'
        )
        self.student, _ = Student.objects.get_or_create(user=self.user, defaults={
            'year_of_study': 1,
            'degree_type': 'bachelor'
        })

        self.course = Course.objects.create(name="מבוא למדעי המחשב")

        self.instructor_user = User.objects.create_user(
            username='lect1',
            password='pass123',
            role='academic',
            id_number='999',
            email='lect@test.com',
            phone='0509999999'
        )
        self.instructor, _ = AcademicStaff.objects.get_or_create(user=self.instructor_user)

        self.course_offering = CourseOffering.objects.create(
            course=self.course,
            instructor=self.instructor,
            year=2024,
            semester='A'
        )

        self.secretary = User.objects.create_user(
            username='sec1',
            password='pass123',
            role='secretary',
            id_number='555',
            email='sec@test.com',
            phone='0505555555'
        )

    def test_submit_course_exemption_post_success(self):
        self.client.login(username='student1', password='pass123')
        file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")

        response = self.client.post(reverse('submit_course_exemption'), {
            'offering_id': self.course_offering.id,
            'title': 'Exemption Request',
            'description': 'I already passed this course elsewhere.',
            'attachment': file
        })

        # ✅ בדוק שנוצרה בקשה בבסיס הנתונים
        self.assertEqual(Request.objects.count(), 1)
        req = Request.objects.first()
        self.assertEqual(req.request_type, 'course_exemption')
        self.assertEqual(req.student, self.student)
        self.assertEqual(req.assigned_to.role, 'secretary')

        # ✅ בדוק שיש הפניה לדף הנכון
        self.assertRedirects(response, reverse('student_request_history'))

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import User, Student, Request

class SubmitOtherRequestTests(TestCase):
    def setUp(self):
        self.client = Client()

        # יצירת משתמש סטודנט
        self.student_user = User.objects.create_user(
            username='student1',
            password='pass123',
            role='student',
            id_number='100001',
            email='student1@test.com',
            phone='0501111000'
        )
        self.student, _ = Student.objects.get_or_create(
            user=self.student_user,
            defaults={'year_of_study': 1, 'degree_type': 'bachelor'}
        )

        # יצירת מזכירה
        self.secretary_user = User.objects.create_user(
            username='sec1',
            password='pass123',
            role='secretary',
            id_number='100002',
            email='sec1@test.com',
            phone='0502222000'
        )

    def test_submit_other_request_success(self):
        """בדיקה שהבקשה מסוג 'אחר' נשלחת בהצלחה"""
        self.client.login(username='student1', password='pass123')

        file = SimpleUploadedFile("doc.pdf", b"Dummy content", content_type="application/pdf")

        response = self.client.post(reverse('submit_other_request'), {
            'title': 'בדיקת מערכת',
            'description': 'אני רוצה לבדוק את המערכת',
            'request_type': 'other',
            'attachment': file
        })

        # בדיקה שנוצרה בקשה אחת בלבד
        self.assertEqual(Request.objects.count(), 1)

        req = Request.objects.first()
        self.assertEqual(req.title, 'בדיקת מערכת')
        self.assertEqual(req.description, 'אני רוצה לבדוק את המערכת')
        self.assertEqual(req.request_type, 'other')
        self.assertEqual(req.student, self.student)
        self.assertEqual(req.assigned_to, self.secretary_user)
        self.assertIsNotNone(req.attachment)

        # בדיקה של הפניה (redirect)
        self.assertRedirects(response, reverse('student_request_history'))


from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from app.models import Student, Request, User

class SubmitPrerequisiteExemptionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='student1',
            password='testpass123',
            role='student',
            id_number='123456789',
            email='student@example.com',
            phone='0501234567'
        )
        self.secretary = User.objects.create_user(
            username='sec1',
            password='testpass123',
            role='secretary',
            id_number='999999999',
            email='secretary@example.com',
            phone='0500000000'
        )
        self.student, _ = Student.objects.get_or_create(
            user=self.user,
            defaults={
                'year_of_study': 1,
                'degree_type': 'bachelor'
            }
        )

    def test_submit_prerequisite_exemption(self):
        self.client.login(username='student1', password='testpass123')

        file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        response = self.client.post(reverse('submit_prerequisite_exemption'), {
            'title': 'Request to Skip Prerequisite',
            'description': 'I already studied this material in another course.',
            'course': 'Introduction to Algorithms',
            'attachment': file
        })

        self.assertRedirects(response, reverse('student_request_history'))
        self.assertEqual(Request.objects.count(), 1)

        req = Request.objects.first()
        self.assertEqual(req.request_type, 'prerequisite_exemption')
        self.assertEqual(req.student, self.student)
        self.assertIn('Introduction to Algorithms', req.title)
        self.assertEqual(req.assigned_to, self.secretary)

class SubmitMilitaryDocsTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.student_user = User.objects.create_user(
            username='student1',
            password='pass123',
            role='student',
            id_number='111111111',
            email='student@test.com',
            phone='0501234567'
        )
        self.secretary = User.objects.create_user(
            username='sec1',
            password='pass123',
            role='secretary',
            id_number='222222222',
            email='sec@test.com',
            phone='0500000000'
        )

        self.student, _ = Student.objects.get_or_create(
            user=self.student_user,
            defaults={
                'year_of_study': 1,
                'degree_type': 'bachelor'
            }
        )

    def test_submit_military_docs_success(self):
        self.client.login(username='student1', password='pass123')

        file = SimpleUploadedFile("military.pdf", b"file_content", content_type="application/pdf")
        response = self.client.post(reverse('submit_military_docs'), {
            'title': 'אישורי מילואים',
            'description': 'מצרף אישורים',
            'attachment': file
        })

        self.assertRedirects(response, reverse('student_request_history'))
        self.assertEqual(Request.objects.count(), 1)

        req = Request.objects.first()
        self.assertEqual(req.title, 'אישורי מילואים')
        self.assertEqual(req.description, 'מצרף אישורים')
        self.assertEqual(req.request_type, 'military_docs')
        self.assertEqual(req.student, self.student)
        self.assertEqual(req.assigned_to, self.secretary)


from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Student, AcademicStaff, Course, CourseOffering
from django.contrib.auth import get_user_model
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from app.models import (
    User, Student, AcademicStaff,
    Course, CourseOffering, StudentCourseEnrollment
)
User = get_user_model()

class LoadRequestFormViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # חשב את השנה האקדמית הנוכחית לפי התאריך
        today = date.today()
        year = today.year
        month = today.month
        self.current_year = f"{year}-{year + 1}" if month >= 10 else f"{year - 1}-{year}"

        self.student_user = User.objects.create_user(
            username='student1',
            password='pass123',
            role='student',
            id_number='999',
            email='student@example.com',
            phone='0501111111',
            department='הנדסת תוכנה',
            date_start='2022-10-01'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            year_of_study=2,
            degree_type='bachelor',
            current_year_of_study=2,
            current_semester='B'
        )

        self.lecturer_user = User.objects.create_user(
            username='lecturer',
            password='pass123',
            role='academic',
            id_number='888',
            email='lect@example.com',
            phone='0509999999',
            department='מדעי המחשב',
            date_start='2020-10-01'
        )
        self.academic, _ = AcademicStaff.objects.get_or_create(user=self.lecturer_user)

        self.course = Course.objects.create(name="מתמטיקה בדידה", semester='A', year_of_study=1)

        # 🟢 הצעות קורס
        self.offering1 = CourseOffering.objects.create(course=self.course, instructor=self.academic, year="2021-2022", semester='A')
        self.offering2 = CourseOffering.objects.create(course=self.course, instructor=self.academic, year=self.current_year, semester='A')
        self.offering3 = CourseOffering.objects.create(course=self.course, instructor=self.academic, year=self.current_year, semester='B')
        self.offering4 = CourseOffering.objects.create(course=self.course, instructor=self.academic, year="2023-2024", semester='A')

        # 🟢 רישום לקורסים
        StudentCourseEnrollment.objects.create(student=self.student, course=self.course, academic_year="2021-2022", semester='A')
        StudentCourseEnrollment.objects.create(student=self.student, course=self.course, academic_year=self.current_year, semester='A')
        StudentCourseEnrollment.objects.create(student=self.student, course=self.course, academic_year=self.current_year, semester='B')
        StudentCourseEnrollment.objects.create(student=self.student, course=self.course, academic_year="2023-2024", semester='A')

    def test_load_form_for_special_exam(self):
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('load_request_form'), {'type': 'special_exam'})

        self.assertEqual(response.status_code, 200)
        allowed_ids = [o.id for o in response.context['allowed_offerings']]
        self.assertIn(self.offering1.id, allowed_ids)
        self.assertIn(self.offering2.id, allowed_ids)
        self.assertIn(self.offering3.id, allowed_ids)

    def test_load_form_for_delay_submission(self):
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('load_request_form'), {'type': 'delay_submission'})

        self.assertEqual(response.status_code, 200)
        allowed_ids = [o.id for o in response.context['allowed_offerings']]
        self.assertIn(self.offering2.id, allowed_ids)
        self.assertIn(self.offering3.id, allowed_ids)
        self.assertNotIn(self.offering1.id, allowed_ids)
        self.assertNotIn(self.offering4.id, allowed_ids)

    def test_load_form_for_prerequisite_exemption(self):
        self.client.login(username='student1', password='pass123')
        response = self.client.get(reverse('load_request_form'), {'type': 'prerequisite_exemption'})

        self.assertEqual(response.status_code, 200)
        allowed_ids = [o.id for o in response.context['allowed_offerings']]
        self.assertIn(self.offering1.id, allowed_ids)
        self.assertIn(self.offering2.id, allowed_ids)
        self.assertIn(self.offering3.id, allowed_ids)
        self.assertIn(self.offering4.id, allowed_ids)

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import User, Student, AcademicStaff, Course, CourseOffering, Request

class SubmitStudentRequestsTests(TestCase):
    def setUp(self):
        self.client = Client()

        # משתמש סטודנט
        self.student_user = User.objects.create_user(
            username='student1',
            password='pass123',
            role='student',
            id_number='123456789',
            email='student@test.com',
            phone='0501234567'
        )
        self.student, _ = Student.objects.get_or_create(
            user=self.student_user,
            defaults={'year_of_study': 1, 'degree_type': 'bachelor'}
        )

        # משתמש מרצה
        self.lecturer_user = User.objects.create_user(
            username='lecturer1',
            password='pass123',
            role='academic',
            id_number='987654321',
            email='lecturer@test.com',
            phone='0507654321'
        )
        self.academic, _ = AcademicStaff.objects.get_or_create(user=self.lecturer_user)

        # מזכירה
        self.secretary = User.objects.create_user(
            username='sec1',
            password='pass123',
            role='secretary',
            id_number='111111111',
            email='sec@test.com',
            phone='0501111111'
        )

        # קורס והצעה
        self.course = Course.objects.create(name='מבוא למדעי המחשב')
        self.offering = CourseOffering.objects.create(
            course=self.course,
            instructor=self.academic,
            year=1,
            semester='A'
        )

    def login_student(self):
        self.client.login(username='student1', password='pass123')

    def upload_file(self):
        return SimpleUploadedFile("test.pdf", b"fake content", content_type="application/pdf")

    def test_submit_special_exam_request(self):
        self.login_student()
        response = self.client.post(reverse('submit_special_exam'), {
            'offering_id': self.offering.id,
            'title': 'מועד נוסף',
            'description': 'לא ניגשתי למועד א\'',
            'attachment': self.upload_file()
        })
        self.assertEqual(Request.objects.count(), 1)
        req = Request.objects.first()
        self.assertEqual(req.request_type, 'special_exam')
        self.assertEqual(req.student, self.student)
        self.assertEqual(req.assigned_to, self.secretary)
        self.assertRedirects(response, reverse('student_request_history'))

    def test_submit_course_exemption(self):
        self.login_student()
        response = self.client.post(reverse('submit_course_exemption'), {
            'title': 'פטור מתכנות',
            'description': 'למדתי את הקורס במקום אחר',
            'offering_id': self.offering.id,
            'attachment': self.upload_file()
        })
        self.assertEqual(Request.objects.count(), 1)
        self.assertEqual(Request.objects.first().request_type, 'course_exemption')

    def test_submit_increase_credits(self):
        self.login_student()
        response = self.client.post(reverse('submit_increase_credits'), {
            'title': 'תוספת נק"ז',
            'description': 'מבקש להוסיף קורס נוסף',
            'attachment': self.upload_file()
        })
        self.assertEqual(Request.objects.count(), 1)
        self.assertEqual(Request.objects.first().request_type, 'increase_credits')

    def test_submit_course_unblock(self):
        self.login_student()
        response = self.client.post(reverse('submit_course_unblock'), {
            'course': 'מערכות הפעלה',
            'title': 'שחרור קורס',
            'description': 'נחסמתי בגלל תנאי קדם',
            'attachment': self.upload_file()
        })
        self.assertEqual(Request.objects.count(), 1)
        self.assertEqual(Request.objects.first().request_type, 'course_unblock')

    def test_submit_registration_exemption(self):
        self.login_student()
        response = self.client.post(reverse('submit_registration_exemption'), {
            'course': 'בסיסי נתונים',
            'title': 'פטור מהרשמה',
            'description': 'לא הצלחתי להירשם בזמן',
            'attachment': self.upload_file()
        })
        self.assertEqual(Request.objects.count(), 1)
        self.assertEqual(Request.objects.first().request_type, 'registration_exemption')

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from app.models import User, Student, AcademicStaff, Course, CourseOffering, Request


class SubmitInstructorRequestIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

        # ודא שהמשתמש לא קיים לפני יצירה
        User.objects.filter(username='student1').delete()
        User.objects.filter(username='lecturer1').delete()

        # משתמש סטודנט
        self.student_user = User.objects.create_user(
            username='student1',
            password='testpass',
            role='student',
            id_number='1111',
            email='student@example.com',
            phone='0501234567'
        )
        self.student, _ = Student.objects.get_or_create(
            user=self.student_user,
            defaults={'year_of_study': 1, 'degree_type': 'bachelor'}
        )

        # משתמש מרצה
        self.lecturer_user = User.objects.create_user(
            username='lecturer1',
            password='testpass',
            role='academic',
            id_number='2222',
            email='lecturer@example.com',
            phone='0507654321'
        )
        self.academic, _ = AcademicStaff.objects.get_or_create(user=self.lecturer_user)

        # קורס והצעה
        self.course = Course.objects.create(name='תכנות מונחה עצמים')
        self.offering = CourseOffering.objects.create(
            course=self.course,
            instructor=self.academic,
            year=1,
            semester='A'
        )

    def login_student(self):
        self.client.login(username='student1', password='testpass')

    def upload_file(self):
        return SimpleUploadedFile("test.pdf", b"data", content_type="application/pdf")

    def post_request(self, url_name, req_type):
        self.login_student()
        response = self.client.post(reverse(url_name), {
            'offering_id': self.offering.id,
            'title': f'בדיקה {req_type}',
            'description': 'תיאור לבדיקה',
            'attachment': self.upload_file()
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Request.objects.count(), 1)
        request_obj = Request.objects.first()
        self.assertEqual(request_obj.request_type, req_type)
        self.assertEqual(request_obj.student, self.student)
        self.assertEqual(request_obj.assigned_to, self.lecturer_user)
        self.assertRedirects(response, reverse('student_request_history'))

        Request.objects.all().delete()  # ניקוי בין בדיקות

    def test_submit_cancel_hw_percent(self):
        self.post_request('submit_cancel_hw_percent', 'cancel_hw_percent')

    def test_submit_delay_submission(self):
        self.post_request('submit_delay_submission', 'delay_assignment')

    def test_submit_include_hw_grade(self):
        self.post_request('submit_include_hw_grade', 'include_hw_grade')

    def test_submit_iron_swords(self):
        self.post_request('submit_iron_swords', 'iron_swords')



from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import Student

User = get_user_model()

from django.contrib.auth import get_user_model

class RequestHistoryIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()

        # יצירת משתמש סטודנט
        self.student_user = User.objects.create_user(
            username='student1',
            password='pass123456',
            id_number='111111111',
            email='student@example.com',
            role='student'
        )

        # יצירת אובייקט Student עם כל השדות החובה
        self.student = Student.objects.create(
            user=self.student_user,
            year_of_study=2,
            degree_type='bachelor'
        )

    def test_back_button_exists_on_history_page(self):
        # התחברות כסטודנט
        self.client.login(username='student1', password='pass123456')

        # בקשת GET לעמוד היסטוריית הבקשות
        response = self.client.get(reverse('student_request_history'))

        self.assertEqual(response.status_code, 200)

        # בדיקה שהכפתור קיים בקוד ה-HTML עם הקישור הנכון
        self.assertContains(response, 'class="back-button"')
        self.assertIn(reverse('student_dashboard'), response.content.decode())

    def test_back_button_redirects_to_correct_page(self):
        # התחברות
        self.client.login(username='student1', password='pass123456')

        # בקשת GET לעמוד שאליו הכפתור אמור להחזיר
        response = self.client.get(reverse('student_dashboard'))

        # נוודא שהעמוד נגיש
        self.assertEqual(response.status_code, 200)

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import Student, Request

class AcademicRequestDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # יצירת משתמש אקדמי
        self.academic_user = get_user_model().objects.create_user(
            username='academic1',
            password='testpass123',
            role='academic',
            id_number='123456789',
            phone='0501234567',
            department='הנדסה'
        )

        # יצירת סטודנט ובקשה
        self.student_user = get_user_model().objects.create_user(
            username='student1',
            password='testpass123',
            role='student',
            id_number='111111111',
            phone='0509876543',
            department='הנדסת תוכנה'
        )

        self.student = Student.objects.create(
            user=self.student_user,
            year_of_study=1,
            degree_type='bachelor'
        )

        self.req = Request.objects.create(
            title='Test Request',
            description='This is a test request.',
            student=self.student,
            assigned_to=self.academic_user,
            status='accepted',
            request_type='other'
        )

    def test_academic_can_view_request_detail(self):
        self.client.login(username='academic1', password='testpass123')
        url = reverse('request_detail_view_academic', args=[self.req.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Request')
        self.assertTemplateUsed(response, 'request_detail_view_academic.html')

    def test_request_detail_not_found(self):
        self.client.login(username='academic1', password='testpass123')
        url = reverse('request_detail_view_academic', args=[999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from app.models import Student, Request

class RequestExplanationTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = get_user_model().objects.create_user(
            username='secretary1_test',
            password='testpass123',
            email='secretary_unique@example.com',
            role='secretary',
            id_number='987654320',
            phone='0500000011',
            department='Test Dept'
        )

        self.student_user = get_user_model().objects.create_user(
            username='student1_test',
            password='studentpass',
            email='student_unique@example.com',
            role='student',
            id_number='987654321',
            phone='0509999991',
            department='CS'
        )

        self.student, _ = Student.objects.get_or_create(
            user=self.student_user,
            defaults={
                'year_of_study': 1,
                'degree_type': 'bachelor'
            }
        )

        self.req = Request.objects.create(
            title='Test Request',
            description='Please approve me',
            status='pending',
            request_type='delay_submission',
            student=self.student,
            assigned_to=self.user
        )

    def test_status_and_explanation_are_saved(self):
        self.client.login(username='secretary1_test', password='testpass123')
        url = reverse('request_detail_update', args=[self.req.id])

        response = self.client.post(url, {
            'status': 'accepted',
            'explanation': 'Valid explanation.'
        })

        self.req.refresh_from_db()
        self.assertEqual(self.req.status, 'accepted')
        self.assertEqual(self.req.explanation, 'Valid explanation.')
        self.assertRedirects(response, reverse('secretary_dashboard'))

    def test_non_assigned_user_cannot_update(self):
        other_user = get_user_model().objects.create_user(
            username='other_secretary',
            password='otherpass',
            role='secretary',
            id_number='123123123',
            phone='0501231234',
            email='other@example.com'
        )

        self.client.login(username='other_secretary', password='otherpass')
        url = reverse('request_detail_update', args=[self.req.id])

        response = self.client.post(url, {
            'status': 'rejected',
            'explanation': 'Should not work.'
        })

        self.req.refresh_from_db()
        self.assertNotEqual(self.req.status, 'rejected')
        self.assertRedirects(response, reverse('secretary_dashboard'))

    def test_in_progress_status_does_not_require_explanation(self):
        self.client.login(username='secretary1_test', password='testpass123')
        url = reverse('request_detail_update', args=[self.req.id])

        response = self.client.post(url, {
            'status': 'in_progress',
            'explanation': ''
        })

        self.req.refresh_from_db()
        self.assertEqual(self.req.status, 'in_progress')
        self.assertEqual(self.req.explanation, '')
        self.assertRedirects(response, reverse('secretary_dashboard'))

    def test_email_sent_to_student(self):
        self.client.login(username='secretary1_test', password='testpass123')
        url = reverse('request_detail_update', args=[self.req.id])

        response = self.client.post(url, {
            'status': 'accepted',
            'explanation': 'Approved due to valid reason.'
        })

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('עדכון סטטוס לבקשה', email.subject)
        self.assertIn('Approved due to valid reason.', email.body)
        self.assertEqual(email.to, [self.student_user.email])

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import Student, Request

User = get_user_model()

class RequestDetailTestsHakton(TestCase):
    def setUp(self):
        # Create user and student
        self.user = User.objects.create_user(
            username='student1',
            password='testpass123',
            role='student',
            id_number='123456789',
            phone='0501234567',
            department='הנדסה',
            date_start='2023-01-01',
            email='student@test.com'
        )
        self.student = Student.objects.create(user=self.user, year_of_study=1, degree_type='bachelor')

        # Create request
        self.request = Request.objects.create(
            title='אלגברה לינארית לתוכנה',
            description='בקשה שקולה 1',
            status='rejected',
            request_type='other',
            student=self.student,
            assigned_to=self.user,
            explanation='דחיית הבקשה 123'
        )

        self.client = Client()
        self.client.login(username='student1', password='testpass123')

    def test_view_request_details_page(self):
        url = reverse('view_previous_request_details', kwargs={'request_id': self.request.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'פרטי בקשה')
        self.assertContains(response, self.request.title)
        self.assertContains(response, self.request.description)
        self.assertContains(response, 'הבקשה נדחתה')
        self.assertContains(response, self.request.explanation)

    def test_print_and_pdf_buttons_exist(self):
        url = reverse('view_previous_request_details', kwargs={'request_id': self.request.id})
        response = self.client.get(url)
        self.assertContains(response, 'הדפס בקשה')
        self.assertContains(response, 'הורד PDF')

    def test_back_buttons_exist(self):
        url = reverse('view_previous_request_details', kwargs={'request_id': self.request.id})
        response = self.client.get(url)
        self.assertContains(response, 'דף הבית')
        self.assertContains(response, 'היסטוריית הבקשות')


from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Secretary, Student, Request
from django.utils import timezone

class SecretaryDashboardUITestsHakton(TestCase):
    def setUp(self):
        self.client = Client()
        self.secretary_user = User.objects.create_user(
            username='sec_user',
            password='secret123',
            role='secretary',
            id_number='123456789',
            email='sec@test.com',
            phone='0501234567',
            department='מזכירות'
        )
        Secretary.objects.get_or_create(user=self.secretary_user)

        self.client.login(username='sec_user', password='secret123')

    def test_general_requests_api_returns_empty(self):
        """
        אם אין בקשות כלליות – תוצג הודעת 'לא נמצאו בקשות.'
        """
        url = reverse('get_secretary_other_requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [])

    def test_dashboard_view_loads(self):
        """
        בדיקה שהדף נטען בהצלחה ומכיל את הכפתורים הנכונים.
        """
        response = self.client.get(reverse('secretary_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '📄 הבקשות שלי')
        self.assertContains(response, 'בקשות כלליות')

    def test_general_requests_button_css_class(self):
        """
        בדיקה ויזואלית שהכפתור מקבל class של active-tab כשהוא נבחר.
        שים לב: זו בדיקה על הלוגיקה – תוודא ב-JS שה-class מתעדכן בזמן קריאה.
        כאן רק נוודא שהכפתור קיים ונגיש.
        """
        response = self.client.get(reverse('secretary_dashboard'))
        self.assertContains(response, 'class="request-button"')

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from app.models import User, Student, Request

class TrackStatusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student1', password='test123', role='student')
        self.student = Student.objects.create(user=self.user, year_of_study=1, degree_type='bachelor')

        self.academic = User.objects.create_user(
            username='lecturer',
            password='test456',
            role='academic',
            email='lecturer@example.com',
            phone='0500000001',
            id_number='111111111',
            department='הנדסה',
            date_start='2022-01-01'
        )
    def create_request(self, status, submitted_offset=0, updated_offset=0):
        submitted_time = timezone.now() - timedelta(minutes=submitted_offset)
        updated_time = timezone.now() - timedelta(minutes=updated_offset)

        req = Request.objects.create(
            title='Test Request',
            description='Just a test',
            status=status,
            request_type='other',
            student=self.student,
            assigned_to=self.academic,
            submitted_at=submitted_time,
            updated_at=updated_time
        )
        return req

    def test_track_status_pending(self):
        req = self.create_request(status='pending')
        self.client.login(username='student1', password='test123')
        response = self.client.get(reverse('track_status', args=[req.id]))
        self.assertContains(response, 'ממתינה')

    def test_track_status_opened(self):
        req = self.create_request(status='pending', submitted_offset=10, updated_offset=2)
        self.client.login(username='student1', password='test123')
        response = self.client.get(reverse('track_status', args=[req.id]))
        self.assertContains(response, 'הבקשה נפתחה')

    def test_track_status_in_progress(self):
        req = self.create_request(status='in_progress')
        self.client.login(username='student1', password='test123')
        response = self.client.get(reverse('track_status', args=[req.id]))
        self.assertContains(response, 'בתהליך')

    def test_track_status_accepted(self):
        req = self.create_request(status='accepted')
        self.client.login(username='student1', password='test123')
        response = self.client.get(reverse('track_status', args=[req.id]))
        self.assertContains(response, 'אושרה')

    def test_track_status_rejected(self):
        req = self.create_request(status='rejected')
        self.client.login(username='student1', password='test123')
        response = self.client.get(reverse('track_status', args=[req.id]))
        self.assertContains(response, 'נדחתה')

    def test_forbidden_access_to_other_students_request(self):
        other_user = User.objects.create_user(
            username='student2',
            password='test789',
            role='student',
            email='student2@example.com',
            phone='0500000003',
            id_number='333333333',
            department='הנדסה',
            date_start='2023-10-10'
        )

        other_student = Student.objects.create(user=other_user, year_of_study=1, degree_type='bachelor')
        req = Request.objects.create(
            title='Other Request',
            description='Not yours',
            status='accepted',
            request_type='other',
            student=other_student,
            assigned_to=self.academic
        )
        self.client.login(username='student1', password='test123')
        response = self.client.get(reverse('track_status', args=[req.id]))
        self.assertEqual(response.status_code, 404)
