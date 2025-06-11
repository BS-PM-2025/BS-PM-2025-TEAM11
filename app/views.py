from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Request

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from app.models import Request, Student

from .models import User
from django.http import JsonResponse
from .models import Course  # adjust this based on your actual model

from .models import Request, CourseOffering
from django.db.models import F

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
    requests = Request.objects.filter(
        assigned_to=request.user,
        status__in=['accepted', 'rejected', 'in_progress']
    ).order_by('-submitted_at')

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


from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Request, Student

@login_required
@never_cache
def student_request_history_view(request):
    status_filter = request.GET.get('status')
    requests_qs = []

    try:
        student_profile = Student.objects.get(user=request.user)
        requests_qs = Request.objects.filter(student=student_profile)

        if status_filter in ['pending', 'accepted', 'rejected', 'in_progress']:
            requests_qs = requests_qs.filter(status=status_filter)

        requests_qs = requests_qs.order_by('-submitted_at')

    except Student.DoesNotExist:
        requests_qs = []  # fallback if student not found

    # ✅ Always respond with valid HttpResponse
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [
            {
                'id': req.id,
                'status': req.status,
                'title': req.title,
                'submitted_at': req.submitted_at.strftime('%d/%m/%Y')
            }
            for req in requests_qs
        ]
        return JsonResponse({'requests': data})

    return render(request, 'student_request_history.html', {
        'requests': requests_qs,
        'selected_status': status_filter
    })





from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from app.models import Request

@login_required
@never_cache
def secretary_requests_api(request):
    user = request.user
    status = request.GET.get("status", "pending")
    filter_type = request.GET.get("type")
    filter_year = request.GET.get("year")
    filter_semester = request.GET.get("semester")
    filter_course = request.GET.get("course")

    all_requests = Request.objects.filter(
        assigned_to=user,
        status=status
    )

    # ❗ סינון שלא יכלול בקשות מסוג "אחר" שעדיין לא הועברו למרצה
    all_requests = all_requests.exclude(
        request_type='other',
        assigned_by__isnull=True  # כלומר עדיין אצל המזכירה המקורית
    )

    filtered = []
    for r in all_requests:
        student = r.student
        course_name = ''
        for c in Course.objects.all():
            if c.name in r.title:
                course_name = c.name
                break

        # Filter by type
        if filter_type:
            if filter_type == 'forwarded_from_secretary' and not r.assigned_by == user:
                continue
            elif filter_type != 'forwarded_from_secretary' and r.request_type != filter_type:
                continue

        # Filter by year
        if filter_year and str(student.current_year_of_study) != filter_year:
            continue

        # Filter by semester
        if filter_semester and student.current_semester != filter_semester:
            continue

        # Filter by course name
        if filter_course and course_name.strip() != filter_course.strip():
            continue

        filtered.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "status": r.status,
            "submitted_at": r.submitted_at,
            "request_type": r.request_type,
            "education_year": student.current_year_of_study,
            "semester": student.current_semester,
            "course_name": course_name,
            "forwarded_from_secretary": r.assigned_by == user
        })

    return JsonResponse(filtered, safe=False)

def secretary_courses_api(request):
    user = request.user
    if user.role != 'secretary':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    all_courses = Course.objects.values_list('name', flat=True).distinct()
    return JsonResponse(sorted(all_courses), safe=False)

@login_required
def academic_requests_api(request):
    user = request.user
    if not hasattr(user, 'role') or user.role != 'academic':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    status = request.GET.get('status')
    if status not in ['pending', 'in_progress', 'accepted', 'rejected']:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    # Optional filters
    request_type = request.GET.get('type')
    year = request.GET.get('year')
    semester = request.GET.get('semester')
    course_name = request.GET.get('course')

    # Start building the query
    requests_qs = Request.objects.filter(
        assigned_to=user,
        status=status
    ).select_related('assigned_by', 'assigned_to', 'student')

    # Filter type
    if request_type:
        if request_type == "forwarded_from_secretary":
            requests_qs = requests_qs.filter(request_type='other', assigned_by__role='secretary')

        else:
            requests_qs = requests_qs.filter(request_type=request_type)

    # Year and semester (from student's current info)
    if year:
        requests_qs = requests_qs.filter(student__current_year_of_study=year)
    if semester:
        requests_qs = requests_qs.filter(student__current_semester=semester)

    # Course (match title or offering)
    if course_name:
        requests_qs = requests_qs.filter(title__icontains=course_name)

    # Serialize the data
    data = []
    for r in requests_qs:
        course_name = extract_course_from_title(r.title)  # make sure this function exists
        data.append({
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'status': r.status,
            'submitted_at': r.submitted_at,
            'request_type': r.request_type,
            'education_year': getattr(r.student, 'current_year_of_study', None),
            'semester': getattr(r.student, 'current_semester', None),
            'course_name': course_name,
            'forwarded_from_secretary': (
                    r.request_type == 'other' and getattr(r.assigned_by, 'role', '') == 'secretary'
            ),
            'debug_info': r.request_type + " | " + str(getattr(r.assigned_to, 'role', ''))  # just for logging

        })

    return JsonResponse(data, safe=False)

def extract_course_from_title(title):
    if not title or '-' not in title:
        return ''
    return title.split('-')[0].strip()


@login_required
def academic_courses_api(request):
    user = request.user
    if user.role != 'academic':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    titles = Request.objects.filter(assigned_to=user).values_list('title', flat=True)
    course_names = set([extract_course_from_title(t) for t in titles if '-' in t])
    return JsonResponse(list(course_names), safe=False)

@login_required
@never_cache
def secretary_dashboard_other(request):
    requests = Request.objects.filter(assigned_to=request.user, status__in=['pending', 'in_progress'])
    return render(request, 'secretary_request_other.html')

@login_required
@never_cache
def get_secretary_other_requests(request):
    requests = Request.objects.filter(
        request_type='other',
        assigned_to=request.user,
        status='pending',
        assigned_to__role='secretary'
    ).exclude(student__user=request.user)  # ✅ הוספת תנאי שמבטיח שלא יכלול בקשות שהמזכירה עצמה העבירה לעצמה

    data = [
        {
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'status': r.status,
            'submitted_at': r.submitted_at,
            'student_id': r.student.id_number,
            'student_username': r.student.user.username,
            'student_phone': r.student.phone
        }
        for r in requests

    ]
    return JsonResponse(data, safe=False)


@login_required
@never_cache
def secretary_requests_other_api(request):
    if request.user.role != 'secretary':
        return JsonResponse([], safe=False)

    requests = Request.objects.filter(
        assigned_to=request.user,
        request_type='other',
        status='pending'  # ✅ רק בקשות שממתינות אצל המזכירה
    ).order_by('-submitted_at')

    data = [
        {
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'status': r.status,
            'submitted_at': r.submitted_at,
            'student_username': r.student.user.username,
            'student_id': r.student.user.id_number,
            'student_phone': r.student.user.phone,
            'request_type': r.request_type,
            'assigned_to': r.assigned_to.id,
            'secretary_id': request.user.id
        }
        for r in requests
    ]

    return JsonResponse(data, safe=False)

def logout_view(request):
    logout(request)
    return redirect('login')

def logout_confirmed(request):
    if request.user.is_authenticated:
        print(f"🔒 Logout confirmed for user: {request.user.username}")
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
from .models import Course

from .models import User, Student, StudentCourseEnrollment,CourseOffering
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
                            StudentCourseEnrollment.objects.create(
                                student=student,
                                course=course,
                                academic_year=academic_year,
                                semester=semester_code
                            )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


from django.core.files.storage import FileSystemStorage

@login_required
def submit_other_request(request):
    if request.method == 'POST':
        student = Student.objects.get(user=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        request_type = request.POST.get('request_type', 'other')

        attachment = request.FILES.get('attachment')
        secretary = User.objects.filter(role='secretary').first()

        new_request = Request.objects.create(
            title=title,
            description=description,
            request_type=request_type,
            student=student,
            assigned_to=secretary,
            attachment=attachment if attachment else None
        )

        return redirect('student_request_history')  # ✅ הפניה להיסטוריה של הסטודנט

from django.shortcuts import get_object_or_404

@login_required
def submit_prerequisite_exemption(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        course_id = request.POST.get('course_id')
        attachment = request.FILES.get('attachment')

        course = get_object_or_404(Course, id=course_id)
        full_title = f"{course.name} | {title}"
        secretary = User.objects.filter(role='secretary').first()

        Request.objects.create(
            title=full_title,
            description=description,
            request_type='prerequisite_exemption',
            student=student,
            assigned_to=secretary,
            attachment=attachment if attachment else None
        )
        return redirect('student_request_history')



@login_required
def submit_military_docs(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')
        secretary = User.objects.filter(role='secretary').first()

        Request.objects.create(
            title=title,
            description=description,
            request_type='military_docs',
            student=student,
            assigned_to=secretary,
            attachment=attachment if attachment else None
        )

        return redirect('student_request_history')

from .models import Course, CourseOffering, StudentCourseEnrollment
from datetime import date

@login_required
def load_request_form(request):
    request_type = request.GET.get('type')
    student = Student.objects.get(user=request.user)

    today = date.today()
    year = today.year
    month = today.month

    if month >= 10:
        current_year = f"{year}-{year + 1}"
    else:
        current_year = f"{year - 1}-{year}"

    current_sem = student.current_semester or 'A'
    all_enrollments = StudentCourseEnrollment.objects.filter(student=student)
    all_offerings = CourseOffering.objects.filter(
        course__in=[e.course for e in all_enrollments],
        year__in=[e.academic_year for e in all_enrollments],
        semester__in=[e.semester for e in all_enrollments]
    )

    allowed_offerings = []

    if request_type == 'special_exam':
        # כל ההרשמות של הסטודנט בשנים קודמות + השנה הנוכחית (עד הסמסטר הנוכחי)
        relevant_enrollments = []
        for enrollment in all_enrollments:
            if enrollment.academic_year < current_year:
                relevant_enrollments.append(enrollment)
            elif enrollment.academic_year == current_year:
                if current_sem == 'A' and enrollment.semester == 'A':
                    relevant_enrollments.append(enrollment)
                elif current_sem == 'B':
                    relevant_enrollments.append(enrollment)

        # קבלת שמות הקורסים הייחודיים מתוך ההרשמות
        course_names = sorted(set(e.course.name for e in relevant_enrollments))

        context = {
            'request_type': request_type,
            'course_names': course_names
        }
        return render(request, f'requests_forms/{request_type}.html', context)


    elif request_type in ['delay_submission', 'cancel_hw_percent', 'include_hw_grade', 'iron_swords']:

        for enrollment in all_enrollments:
            if (
                enrollment.academic_year == current_year and
                enrollment.semester == current_sem
            ):
                matching_offerings = CourseOffering.objects.filter(
                    course=enrollment.course,
                    year=current_year,
                    semester=current_sem
                )
                allowed_offerings.extend(matching_offerings)


    elif request_type in ['prerequisite_exemption', 'course_exemption', 'course_unblock', 'registration_exemption']:

        allowed_courses = Course.objects.all().order_by('name')  # ⬅️ שורת הקסם

        context = {

            'request_type': request_type,

            'allowed_courses': allowed_courses

        }

        return render(request, f'requests_forms/{request_type}.html', context)


    context = {
        'request_type': request_type,
        'allowed_offerings': allowed_offerings
    }
    return render(request, f'requests_forms/{request_type}.html', context)


from django.shortcuts import get_object_or_404
from .models import Request, Student, CourseOffering, User

@login_required
def submit_special_exam(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        selected_course_name = request.POST.get('course_name')  # שם הקורס שנבחר
        attachment = request.FILES.get('attachment')

        # שליפת קורס לפי שם
        course = get_object_or_404(Course, name=selected_course_name)

        # שליפת המזכירה הראשונה
        secretary = User.objects.filter(role='secretary').first()

        # יצירת הבקשה (בלי מרצה)
        Request.objects.create(
            title=f"{course.name} | {title}",
            description=description,
            request_type='special_exam',
            student=student,
            assigned_to=secretary,
            attachment=attachment if attachment else None
        )

        return redirect('student_request_history')



@login_required
def submit_course_exemption(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        title = request.POST.get('title')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')

        full_title = f"{course.name} | {title}"
        secretary = User.objects.filter(role='secretary').first()

        Request.objects.create(
            title=full_title,
            description=description,
            request_type='course_exemption',
            student=student,
            assigned_to=secretary,
            attachment=attachment if attachment else None
        )
        return redirect('student_request_history')

@login_required
def submit_increase_credits(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')
        request_type = 'increase_credits'

        secretary = User.objects.filter(role='secretary').first()

        Request.objects.create(
            title=title,
            description=description,
            request_type=request_type,
            student=student,
            assigned_to=secretary,
            attachment=attachment if attachment else None
        )

        return redirect('student_request_history')

@login_required
def submit_course_unblock(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        title = request.POST.get('title')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')

        full_title = f"{course.name} | {title}"
        secretary = User.objects.filter(role='secretary').first()

        Request.objects.create(
            title=full_title,
            description=description,
            request_type='course_unblock',
            student=student,
            assigned_to=secretary,
            attachment=attachment if attachment else None
        )
        return redirect('student_request_history')

@login_required
def submit_registration_exemption(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        title = request.POST.get('title')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')

        full_title = f"{course.name} | {title}"
        secretary = User.objects.filter(role='secretary').first()

        Request.objects.create(
            title=full_title,
            description=description,
            request_type='registration_exemption',
            student=student,
            assigned_to=secretary,
            attachment=attachment if attachment else None
        )
        return redirect('student_request_history')

@login_required
def submit_cancel_hw_percent(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        course_offering_id = request.POST.get('offering_id')
        attachment = request.FILES.get('attachment')

        course_offering = get_object_or_404(CourseOffering, id=course_offering_id)
        lecturer = course_offering.instructor.user

        full_title = f"{course_offering.course.name} - {lecturer.get_full_name()} | {title}"

        Request.objects.create(
            title=full_title,
            description=description,
            request_type='cancel_hw_percent',
            student=student,
            assigned_to=lecturer,
            attachment=attachment if attachment else None
        )

        return redirect('student_request_history')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from app.models import Student, CourseOffering, User, Request


@login_required
def submit_delay_submission(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        course_offering_id = request.POST.get('offering_id')
        attachment = request.FILES.get('attachment')

        course_offering = get_object_or_404(CourseOffering, id=course_offering_id)
        lecturer = course_offering.instructor.user  # המרצה האחראי

        full_title = f"{course_offering.course.name} - {lecturer.get_full_name()} | {title}"

        Request.objects.create(
            title=full_title,
            description=description,
            request_type='delay_submission',
            student=student,
            assigned_to=lecturer,  # נשלח למרצה
            attachment=attachment if attachment else None
        )

        return redirect('student_request_history')


@login_required
def submit_include_hw_grade(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        offering_id = request.POST.get('offering_id')
        attachment = request.FILES.get('attachment')

        course_offering = get_object_or_404(CourseOffering, id=offering_id)
        instructor = course_offering.instructor.user

        full_title = f"{course_offering.course.name} - {instructor.get_full_name()} | {title}"

        Request.objects.create(
            title=full_title,
            description=description,
            request_type='include_hw_grade',
            student=student,
            assigned_to=instructor,
            attachment=attachment if attachment else None
        )

        return redirect('student_request_history')

@login_required
def submit_iron_swords(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        title = request.POST.get('title')
        description = request.POST.get('description')
        offering_id = request.POST.get('offering_id')
        attachment = request.FILES.get('attachment')

        course_offering = get_object_or_404(CourseOffering, id=offering_id)
        instructor = course_offering.instructor.user

        full_title = f"{course_offering.course.name} - {instructor.get_full_name()} | {title}"

        Request.objects.create(
            title=full_title,
            description=description,
            request_type='iron_swords',
            student=student,
            assigned_to=instructor,
            attachment=attachment if attachment else None
        )

        return redirect('student_request_history')
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Request
from django.core.mail import send_mail
from django.conf import settings



@login_required
def request_detail_update(request, request_id):
    req = get_object_or_404(Request, id=request_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        explanation = request.POST.get('explanation', '')

        # במקום לבדוק רק את התפקיד
        if req.request_type == 'other' and status in ['accepted', 'rejected']:
            # בדיקה אם היא עדיין אצל המזכירה המקורית
            original_secretary = User.objects.filter(role='secretary').first()
            if req.assigned_to == original_secretary:
                messages.error(request,
                               "לא ניתן לאשר או לדחות בקשה מסוג 'אחר' כל עוד היא אצל המזכירה המקורית. יש להעבירה קודם.")
                return redirect(request.path)


        # ✅ Allow status updates if user is the assigned_to
        if request.user == req.assigned_to:
            req.status = status
            if status != 'in_progress':
                req.explanation = explanation
            req.save()
            # ✅ Set success message
            messages.success(request, "הבקשה טופלה בהצלחה והסטודנט קיבל עדכון בדוא\"ל.")            # ✅ Send email to student
            subject = f"עדכון סטטוס לבקשה: {req.title}"
            status_translations = {
                'accepted': 'אושרה',
                'rejected': 'נדחתה',
                'in_progress': 'בטיפול',
            }
            translated_status = status_translations.get(status, status)
            message = f"""
שלום {req.student.user.username},

הבקשה שלך שכותרתה: "{req.title}" {translated_status}.
{f'הסבר: {explanation}' if explanation else ''}

בברכה,
מערכת ניהול בקשות
            """

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [req.student.user.email],
                fail_silently=False
            )

        # Redirect based on role
        if request.user.role == 'secretary':
            return redirect('secretary_dashboard')
        elif request.user.role == 'academic':
            return redirect('academic_dashboard')
        else:
            return redirect('home')

    return render(request, 'request_detail_update.html', {'req': req})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import Request, User

from app.models import User, Student, Request, AcademicStaff

@login_required
def view_request_details_for_other(request, request_id):
    req = get_object_or_404(Request, id=request_id, request_type='other')

    # ✅ שליפת כל המרצים הקיימים לפי המודל AcademicStaff
    academic_users = [staff.user for staff in AcademicStaff.objects.all()]
    include_secretary = request.user
    success_message = None

    if request.method == 'POST':
        assignee_id = request.POST.get('assignee_id')
        if assignee_id:
            assignee = get_object_or_404(User, id=assignee_id)

            # ✅ תמיד מעדכנים את המטופל החדש, גם אם זו אותה המזכירה
            req.assigned_by = request.user
            req.assigned_to = assignee
            req.status = 'pending'
            # אם מעבירים למזכירה עצמה => עדכן את סוג הבקשה
            if assignee == request.user:
                req.request_type = 'internal_forwarded'
            req.save()

            messages.success(request, "הבקשה הועברה בהצלחה.")
            return redirect('secretary_dashboard_other')

    return render(request, 'view_request_details_for_other.html', {
        'req': req,
        'academic_staff': academic_users,
        'include_secretary': include_secretary
    })

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

@login_required
def view_previous_request_details(request, request_id):
    student = get_object_or_404(Student, user=request.user)
    req = get_object_or_404(Request, id=request_id, student=student)

    if req.status not in ['accepted', 'rejected']:
        raise Http404("Access denied. You can only view completed requests.")

    return render(request, 'view_previous_request_details.html', {
        'req': req
    })


import csv
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import User

@csrf_exempt
def check_email_role(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        # אם קיים כבר במשתמשים
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'exists'})

        # 🔍 חיפוש בקובץ המרצים
        file_path = os.path.join(settings.BASE_DIR, 'app', 'teachers_list.csv')
        try:
            with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    print("🧪 Row:", row)  # הדפסה לבדיקה
                    print("🧪 Keys:", row.keys())
                    if row['email'].strip().lower() == email:
                        return JsonResponse({'status': 'ok', 'role': 'academic'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

        # לא נמצא בשום מקום – סטודנט חדש
        return JsonResponse({'status': 'ok', 'role': 'student'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
import json

from .models import User, AcademicStaff, Course, CourseOffering

@csrf_exempt
def final_academic_registration(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # בדיקות כפילויות בסיסיות
            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({'status': 'error', 'message': 'Email already registered.'})
            if User.objects.filter(id_number=data['id_number']).exists():
                return JsonResponse({'status': 'error', 'message': 'ID already exists.'})
            if User.objects.filter(phone=data['phone']).exists():
                return JsonResponse({'status': 'error', 'message': 'Phone already exists.'})
            if User.objects.filter(username=data['username']).exists():
                return JsonResponse({'status': 'error', 'message': 'Username already exists.'})

            # 1️⃣ יצירת משתמש עם role = academic
            user = User.objects.create(
                username=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                id_number=data['id_number'],
                phone=data['phone'],
                email=data['email'],
                password=make_password(data['password']),
                role='academic'
            )

            # 2️⃣ יצירת AcademicStaff
            academic = AcademicStaff.objects.get(user=user)

            # 3️⃣ קישור לקורסים (courses = רשימת מילונים)
            courses = data.get('courses', [])
            for c in courses:
                course_id = c.get('course_id')
                year = c.get('teaching_year')
                semester = c.get('semester')

                course = Course.objects.filter(id=course_id).first()
                if not course:
                    continue  # אם הקורס לא קיים – מדלגים

                CourseOffering.objects.create(
                    course=course,
                    instructor=academic,
                    year=year,
                    semester=semester
                )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
from django.http import JsonResponse
from .models import Course

def get_all_courses(request):
    courses = Course.objects.all().values('id', 'name')
    return JsonResponse(list(courses), safe=False)


from django.shortcuts import render, get_object_or_404
from app.models import Request

def request_detail_view_academic(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    return render(request, 'request_detail_view_academic.html', {
        'request_obj': req
    })

# views.py
from django.shortcuts import render, get_object_or_404
from .models import Request
from django.contrib.auth.decorators import login_required

@login_required
def track_status(request, request_id):
    req = get_object_or_404(Request, id=request_id, student__user=request.user)

    # נבדוק אם הבקשה נפתחה אבל עדיין בפנדינג
    if req.status == 'pending' and req.updated_at != req.submitted_at:
        effective_status = 'opened'
    else:
        effective_status = req.status

    return render(request, 'track_status.html', {
        'request_status': effective_status
    })
from django.utils import timezone

@login_required
def view_request(request, request_id):
    req = get_object_or_404(Request, id=request_id)

    if req.status == 'pending' and request.user == req.assigned_to:
        # עדכון עדין בלי לשנות שדות נוספים
        req.updated_at = timezone.now()
        req.save(update_fields=['updated_at'])

    return render(request, 'view_request.html', {'req': req})

from django.shortcuts import render, get_object_or_404
from .models import Request

def request_detail_view_secretary(request, request_id):
    request_obj = get_object_or_404(Request, id=request_id)
    return render(request, 'request_detail_view_secretary.html', {'request_obj': request_obj})
