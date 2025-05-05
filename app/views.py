from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Request
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from app.models import Request, Student

from .models import User


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        if not username or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            print("Authenticated user:", user)  # 🧪 הדפסה לבדיקה
            login(request, user)

            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'secretary':
                return redirect('secretary_dashboard')
            elif user.role == 'academic':
                return redirect('academic_dashboard')
            else:
                messages.error(request, "User role is not recognized.")
        if user is not None:
            login(request, user)

            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'secretary':
                return redirect('secretary_dashboard')
            elif user.role == 'academic':
                return redirect('academic_dashboard')
            else:
                messages.error(request, "User role is not recognized.")
        else:
            messages.error(request, "Invalid username or password.")


    return render(request, 'login.html')


@login_required
@never_cache
def student_dashboard(request):
    return render(request, 'student_dashboard.html')
@login_required
@never_cache
def secretary_dashboard(request):
    return render(request, 'secretary_dashboard.html')
@login_required
@never_cache
def academic_dashboard(request):
    return render(request, 'academic_dashboard.html')
@login_required
@never_cache
def academic_request_history_view(request):
    return render(request, 'academic_request_history.html')
@login_required
@never_cache
def secretary_request_history_view(request):
    return render(request, 'secretary_request_history.html')
@login_required
@never_cache

def categorized_requests_api(request):
    status = request.GET.get('status')

    if status not in ['pending', 'in_progress', 'accepted', 'rejected']:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    user = request.user

    requests = Request.objects.filter(
        assigned_to=user,
        status=status
    ).values('id', 'title', 'submitted_at', 'status')

    return JsonResponse(list(requests), safe=False)




@login_required
@never_cache
def student_dashboard(request):
    request_types = dict(Request.REQUEST_TYPES)
    return render(request, 'student_dashboard.html', {'request_types': request_types})


@login_required
@never_cache
def student_request_history_view(request):
    try:
        student_profile = Student.objects.get(user=request.user)
        requests = Request.objects.filter(student=student_profile).order_by('-submitted_at')
    except Student.DoesNotExist:
        requests = []
    return render(request, 'student_request_history.html', {'requests': requests})



@login_required

@never_cache
def secretary_requests_api(request):
    user = request.user

    # נביא רק את הבקשות שהן בפנדינג ולא מהסוג other
    requests = Request.objects.filter(
        assigned_to=user,
        status='pending'
    ).exclude(request_type='other')

    data = [{
        'title': r.title,
        'description': r.description,
        'status': r.status,
        'submitted_at': r.submitted_at,
    } for r in requests]

    return JsonResponse(data, safe=False)


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Request

@login_required

@never_cache
def academic_requests_api(request):
    # Get status from query parameters
    status = request.GET.get('status')
    valid_statuses = ['pending', 'in_progress', 'accepted', 'rejected']

    if status not in valid_statuses:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    user = request.user
    # Check that the user has 'academic' role
    if not hasattr(user, 'role') or user.role != 'academic':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Filter requests assigned to this academic user
    requests_qs = Request.objects.filter(assigned_to=user, status=status)

    # Serialize and return data
    data = list(requests_qs.values('id', 'title', 'description', 'status', 'submitted_at'))
    return JsonResponse(data, safe=False)
@login_required
@never_cache
def secretary_dashboard_other(request):
    return render(request, 'secretary_dashboard_other.html')
@login_required

@never_cache
def secretary_requests_other_api(request):
    user = request.user

    requests = Request.objects.filter(
        assigned_to=user,
        request_type='other',
        status='pending'
    )

    data = [
        {
            'title': r.title,
            'description': r.description,
            'status': r.status,
            'submitted_at': r.submitted_at,
        }
        for r in requests
    ]

    return JsonResponse(data, safe=False)

def logout_view(request):
    logout(request)
    return redirect('login')


from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
import random


from django.contrib.auth import get_user_model

def send_verification_code(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if email and email.endswith("@ac.sce.ac.il"):
            User = get_user_model()
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'exists', 'message': 'Email already registered.'})

            # המשך שליחת קוד אימות
            code = random.randint(100000, 999999)
            request.session['verification_code'] = str(code)
            request.session['verified_email'] = email

            send_mail(
                subject="RequestFlow Email Verification",
                message=f"Your verification code is: {code}",
                from_email="requestflow@sce.ac.il",
                recipient_list=[email],
                fail_silently=False,
            )
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def verify_code(request):
    if request.method == "POST":
        user_code = request.POST.get("code")
        real_code = request.session.get("verification_code")
        if user_code == real_code:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'invalid'})
    return JsonResponse({'status': 'error'})

from django.contrib.auth import login


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def check_id_and_phone(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_number = data.get('id_number')
            phone = data.get('phone')

            if User.objects.filter(id_number=id_number).exists():
                return JsonResponse({'status': 'exists', 'message': 'Student ID already exists in the system.'})

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({'status': 'exists', 'message': 'Phone number already exists in the system.'})

            return JsonResponse({'status': 'ok'})  # הכל תקין – אפשר להמשיך
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Course, StudentCourse

from .models import User, Student
@csrf_exempt
def final_student_registration(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 🛑 בדיקה אם המשתמש או הת"ז או הטלפון כבר קיימים
            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({'status': 'error', 'message': 'Email already registered.'})
            if User.objects.filter(id_number=data['id_number']).exists():
                return JsonResponse({'status': 'error', 'message': 'ID already exists.'})
            if User.objects.filter(phone=data['phone']).exists():
                return JsonResponse({'status': 'error', 'message': 'Phone already exists.'})

            # 🧑 יצירת משתמש חדש
            user = User.objects.create(
                username=data['username'],
                id_number=data['id_number'],
                phone=data['phone'],
                email=data['email'],
                password=make_password(data['password']),
                first_name=data['first_name'],
                last_name=data['last_name'],
                role='student'
            )

            # 🎓 יצירת סטודנט (כעת נשמר למשתנה)
            education = data.get('education', {})
            student = Student.objects.create(
                user=user,
                year_of_study=education.get('start_year'),
                degree_type=education.get('degree_type'),
                current_year_of_study=education.get('current_year_of_study'),
                current_semester=education.get('current_semester'),
                year1_sem1=education.get('year1_sem1'),
                year1_sem2=education.get('year1_sem2'),
                year2_sem1=education.get('year2_sem1'),
                year2_sem2=education.get('year2_sem2'),
                year3_sem1=education.get('year3_sem1'),
                year3_sem2=education.get('year3_sem2'),
                year4_sem1=education.get('year4_sem1'),
                year4_sem2=education.get('year4_sem2'),
            )

            # 🧩 שיוך קורסים רלוונטיים לפי שנות לימוד וסמסטרים
            year_sem_map = {
                1: [('year1_sem1', 'A'), ('year1_sem2', 'B')],
                2: [('year2_sem1', 'A'), ('year2_sem2', 'B')],
                3: [('year3_sem1', 'A'), ('year3_sem2', 'B')],
                4: [('year4_sem1', 'A'), ('year4_sem2', 'B')],
            }

            current_year = int(education.get('current_year_of_study', 0))

            for year in range(1, current_year + 1):
                for field_name, semester_code in year_sem_map[year]:
                    academic_year = education.get(field_name)
                    if academic_year:
                        # שליפת קורסים מתאימים לשנה וסמסטר
                        matching_courses = Course.objects.filter(
                            year_of_study=year,
                            semester=semester_code
                        )

                        for course in matching_courses:
                            # יצירת קשר בין סטודנט לקורס
                            StudentCourse.objects.create(
                                student=student,
                                course=course,
                                academic_year=academic_year,
                                semester=semester_code
                            )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
