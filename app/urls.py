from django.urls import path
from . import views
from .views import login_view, student_dashboard, secretary_dashboard, academic_dashboard

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/student/', student_dashboard, name='student_dashboard'),
    path('dashboard/secretary/', secretary_dashboard, name='secretary_dashboard'),
    path('dashboard/academic/', academic_dashboard, name='academic_dashboard'),
]
