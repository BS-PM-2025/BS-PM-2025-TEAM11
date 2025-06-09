from django.urls import path
from . import views
from .views import login_view, student_dashboard, secretary_dashboard, academic_dashboard
from .views import categorized_requests_api

from django.conf import settings
from django.conf.urls.static import static

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
    path('api/requests/secretary/', views.secretary_requests_api, name='secretary_requests_api'),
    path('api/requests/academic/', views.academic_requests_api, name='academic_requests_api'),
    path('api/requests/secretary/other/', views.secretary_requests_other_api, name='secretary_requests_other_api'),
    path('dashboard/secretary/other/', views.secretary_dashboard_other, name='secretary_dashboard_other'),
    # הדף לבקשות OTHER
    path('logout/', views.logout_view, name='logout'),
    path('logout_confirmed/', views.logout_confirmed, name='logout_confirmed'),
    path('api/academic/courses/', views.academic_courses_api, name='academic_courses_api'),

    path('send-verification-code/', views.send_verification_code, name='send_verification_code'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('check-id-and-phone/', views.check_id_and_phone, name='check_id_and_phone'),
    path('final-student-registration/', views.final_student_registration, name='final_student_registration'),
    path('submit/other/', views.submit_other_request, name='submit_other_request'),
    path('load-request-form/', views.load_request_form, name='load_request_form'),
    path('submit/prerequisite-exemption/', views.submit_prerequisite_exemption, name='submit_prerequisite_exemption'),
   path('submit/military_docs/', views.submit_military_docs, name='submit_military_docs'),
    path('submit/special_exam/', views.submit_special_exam, name='submit_special_exam'),
    path('submit/course_exemption/', views.submit_course_exemption, name='submit_course_exemption'),
   path('submit/increase_credits/', views.submit_increase_credits, name='submit_increase_credits'),
   path('submit/course_unblock/', views.submit_course_unblock, name='submit_course_unblock'),
    path('submit/registration_exemption/', views.submit_registration_exemption, name='submit_registration_exemption'),
   path('submit/cancel_hw_percent/', views.submit_cancel_hw_percent, name='submit_cancel_hw_percent'),
    path('submit/delay_submission/', views.submit_delay_submission, name='submit_delay_submission'),
   path('submit/include_hw_grade/', views.submit_include_hw_grade, name='submit_include_hw_grade'),
    path('submit/iron_swords/', views.submit_iron_swords, name='submit_iron_swords'),
   path('api/requests/secretary/other/', views.get_secretary_other_requests, name='get_secretary_other_requests'),
path('secretary/request/other/<int:request_id>/', views.view_request_details_for_other, name='view_request_other'),
path('requests/<int:request_id>/', views.request_detail_update, name='request_detail_update'),
path('student/request-details/<int:request_id>/', views.view_previous_request_details, name='view_previous_request_details'),
path('final-academic-registration/', views.final_academic_registration, name='final_academic_registration'),
    path('check-email-role/', views.check_email_role, name='check_email_role'),
path('get-all-courses/', views.get_all_courses, name='get_all_courses'),
path('requests/<int:request_id>/academic/', views.request_detail_view_academic,name='request_detail_view_academic'),
path('track_status/<int:request_id>/', views.track_status, name='track_status'),
path('requests/<int:request_id>/secretary/', views.request_detail_view_secretary, name='request_detail_view_secretary'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)