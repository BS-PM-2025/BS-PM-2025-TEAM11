from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Student, Secretary, AcademicStaff,Request
from django.contrib import admin
from .models import Course, StudentCourse, CourseInstructor

admin.site.register(CourseInstructor)
admin.site.register(Course)
admin.site.register(StudentCourse)
admin.site.register(User)
admin.site.register(Student)
admin.site.register(Secretary)
admin.site.register(AcademicStaff)
class RequestAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/request_admin.js',)
admin.site.register(Request, RequestAdmin)

