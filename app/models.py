from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError

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
    id_number = models.CharField(max_length=9, unique=True)  # ת"ז מוסדית (מוזנת בהרשמה)
    phone = models.CharField(max_length=10, unique=True)
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
    year1_sem1 = models.CharField(max_length=9, null=True, blank=True)
    year1_sem2 = models.CharField(max_length=9, null=True, blank=True)
    year2_sem1 = models.CharField(max_length=9, null=True, blank=True)
    year2_sem2 = models.CharField(max_length=9, null=True, blank=True)
    year3_sem1 = models.CharField(max_length=9, null=True, blank=True)
    year3_sem2 = models.CharField(max_length=9, null=True, blank=True)
    year4_sem1 = models.CharField(max_length=9, null=True, blank=True)
    year4_sem2 = models.CharField(max_length=9, null=True, blank=True)
    current_year_of_study = models.PositiveIntegerField(null=True, blank=True)
    current_semester = models.CharField(max_length=1, choices=[('A', 'Semester A'), ('B', 'Semester B')], null=True,
                                        blank=True)

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
        ('other', 'אחר'),
        ('cancel_hw_percent', 'ביטול % אחוז עבודות בית בציון הסופי'),
        ('special_exam', 'בקשה למועד מיוחד'),
        ('iron_swords', 'בקשה למטלה חלופית - חרבות ברזל'),
        ('prerequisite_exemption', 'בקשה לפטור מדרישות קדם'),
        ('course_exemption', 'בקשה לפטור מקורס'),
        ('delay_submission', 'דחיית הגשת עבודה'),
        ('increase_credits', 'הגדלת נ"ז מעבר למותר'),
        ('military_docs', 'הגשת אישורי מילואים'),
        ('course_unblock', 'שחרור חסימת קורס'),
        ('registration_exemption', 'שחרור מחובת הרשמה'),
        ('include_hw_grade', 'שקלול עבודות בית בציון הסופי'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES, default='other')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__in': ['academic', 'secretary']})
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # ✅ לא לאפשר אישור או דחיה לסוג 'other'
        if self.request_type == 'other' and self.status in ['accepted', 'rejected']:
            raise ValidationError("Cannot accept or reject a request of type 'Other'. It must be forwarded only.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Request: {self.title} ({self.status})"







class Course(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey(AcademicStaff, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    semester = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B')])

    def __str__(self):
        return f"{self.course.name} - {self.instructor.user.get_full_name()}"


class StudentCourseEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.user.username} - {self.offering}"
