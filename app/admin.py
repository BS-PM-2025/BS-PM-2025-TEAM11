from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Student, Secretary, AcademicStaff,Request,Course, CourseOffering, StudentCourseEnrollment

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Secretary)
admin.site.register(AcademicStaff)
class RequestAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/request_admin.js',)
admin.site.register(Request, RequestAdmin)

# ✅ מוסיפים את אלה:
admin.site.register(Course)
admin.site.register(CourseOffering)
admin.site.register(StudentCourseEnrollment)
