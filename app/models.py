from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model  # ✅ זה כאן ולא בתוך class
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
    assigned_by = models.ForeignKey(  #  Add this here
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests_forwarded'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    explanation = models.TextField(blank=True)

    def clean(self):
        if self.request_type == 'other' and self.status in ['accepted', 'rejected']:
            if self.assigned_to.role == 'secretary':
                raise ValidationError("לא ניתן לאשר או לדחות בקשה מסוג 'אחר' כל עוד היא אצל המזכירה. יש להעבירה קודם.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Request: {self.title} ({self.status})"







class Course(models.Model):
    SEMESTER_CHOICES = [
        ('A', 'סמסטר א'),
        ('B', 'סמסטר ב'),
    ]

    YEAR_OF_STUDY_CHOICES = [
        (1, 'שנה א'),
        (2, 'שנה ב'),
        (3, 'שנה ג'),
        (4, 'שנה ד'),
    ]

    name = models.CharField(max_length=255, verbose_name="שם הקורס")
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, verbose_name="סמסטר לימוד הקורס", null=True)
    year_of_study = models.IntegerField(choices=YEAR_OF_STUDY_CHOICES, verbose_name="שנת לימוד הקורס", null=True)

    def __str__(self):
        return f"{self.name} (שנה {self.year_of_study}, סמסטר {self.semester})"



class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey(AcademicStaff, on_delete=models.CASCADE)
    year = models.CharField(max_length=9)  # כדי לאפשר פורמט "2022-2023"
    semester = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B')])

    def __str__(self):
        return f"{self.course.name} - {self.instructor.user.get_full_name()}"


class StudentCourseEnrollment(models.Model):
    SEMESTER_CHOICES = [
        ('A', 'סמסטר א'),
        ('B', 'סמסטר ב'),
    ]

    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    academic_year = models.CharField(
        max_length=9,
        verbose_name="שנה אקדמית",
        help_text="פורמט: 2022-2023",
        null=True,  # ⬅️ זה השינוי הדרוש!
        blank=True  # ⬅️ כדי לא להכריח למלא בטפסים
    )
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, verbose_name="סמסטר")

    class Meta:
        unique_together = ('student', 'course', 'academic_year', 'semester')

    def __str__(self):
        return f"{self.student.user.id_number} - {self.course.name} ({self.academic_year}, סמסטר {self.semester})"
