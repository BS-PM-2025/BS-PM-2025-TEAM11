from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Student, Secretary, AcademicStaff

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Secretary)
admin.site.register(AcademicStaff)
