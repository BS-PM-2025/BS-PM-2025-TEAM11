from django.urls import path
from . import views
from .views import login_view, student_dashboard, secretary_dashboard, academic_dashboard
from .views import categorized_requests_api


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/student/', student_dashboard, name='student_dashboard'),
    path('dashboard/secretary/', secretary_dashboard, name='secretary_dashboard'),
    path('dashboard/academic/', academic_dashboard, name='academic_dashboard'),
    path('dashboard/academic/requests/history/', views.academic_request_history_view, name='academic_request_history'),
    path('dashboard/secretary/requests/history/', views.secretary_request_history_view, name='secretary_request_history'),
    path('api/requests/', categorized_requests_api, name='categorized_requests_api'),

    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/student/requests/history/', views.student_request_history_view,name='student_request_history'),

]
