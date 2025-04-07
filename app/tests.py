from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import Student, Secretary, AcademicStaff

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
