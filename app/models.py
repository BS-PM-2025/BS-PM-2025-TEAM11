from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('secretary', 'Secretary'),
        ('academic', 'Academic Staff'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    id_number = models.CharField(max_length=10, unique=True)  # ת"ז מוסדית (מוזנת בהרשמה)
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    date_start = models.DateField(null=True, blank=True)

    # נשתמש ב-username המובנה, אבל נדאג שהוא יווצר אוטומטית בהרשמה
    username = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"



class Student(models.Model):
    DEGREE_CHOICES = [
        ('bachelor', 'תואר ראשון'),
        ('master', 'תואר שני'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    year_of_study = models.PositiveIntegerField(verbose_name="year of study")
    degree_type = models.CharField(max_length=10, choices=DEGREE_CHOICES, verbose_name="degree type")

    def __str__(self):
        return f"Student: {self.user.username}"



class AcademicStaff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Academic Staff: {self.user.username}"


class Secretary(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Secretary: {self.user.username}"


class Request(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    REQUEST_TYPES = [
        ('other', 'Other'),
        ('iron_swords', 'Alternative Assignment for Iron Swords'),
        ('delay_submission', 'Assignment Submission Extension'),
        ('course_unblock', 'Course Unblocking'),
        ('cancel_hw_percent', 'Cancel Homework Percentage in Final Grade'),
        ('prerequisite_exemption', 'Prerequisite Exemption'),
        ('increase_credits', 'Credit Limit Increase'),
        ('registration_exemption', 'Exemption from Course Registration'),
        ('special_exam', 'Special Exam Request'),
        ('course_exemption', 'Course Exemption Request'),
        ('military_docs', 'Reserve Duty Documentation'),
        ('include_hw_grade', 'Include Homework in Final Grade'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES, default='other')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__in': ['academic', 'secretary']})
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request: {self.title} ({self.status})"
