from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Request
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Request
from django.contrib import messages
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
@login_required
@never_cache
def secretary_requests_api(request):
    user = request.user

    requests = Request.objects.filter(
        assigned_to=user,
        status='pending'
    ).exclude(request_type='other').order_by('-submitted_at')

    data = [
        {
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'status': r.status,
            'submitted_at': r.submitted_at,
        }
        for r in requests
    ]

    return JsonResponse(data, safe=False)


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Request

@login_required
@never_cache
def academic_requests_api(request):
    user = request.user

    # Validate user is academic staff
    if not hasattr(user, 'role') or user.role != 'academic':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Get optional filter by status
    status = request.GET.get('status')
    valid_statuses = ['pending', 'in_progress', 'accepted', 'rejected']

    if status and status not in valid_statuses:
        return JsonResponse({'error': 'Invalid status filter'}, status=400)

    # Filter by status or return all
    requests_qs = Request.objects.filter(assigned_to=user)
    if status:
        requests_qs = requests_qs.filter(status=status)

    # Serialize
    data = [
        {
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'status': r.status,
            'submitted_at': r.submitted_at,
        }
        for r in requests_qs
    ]
    return JsonResponse(data, safe=False)

@login_required
@never_cache
def secretary_dashboard_other(request):
    return render(request, 'secretary_request_other.html')

@login_required
@never_cache
def get_secretary_other_requests(request):
    requests = Request.objects.filter(request_type='other')
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
def view_request_details_for_other(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    return render(request, 'view_request_details_for_other.html', {'req': req})


@login_required
@never_cache
def secretary_requests_other_api(request):
    if request.user.role != 'secretary':
        return JsonResponse([], safe=False)

    requests = Request.objects.filter(
        assigned_to=request.user,
        request_type='other',
        status='pending'
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
            'student_phone': r.student.user.phone
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
                role='student'  # אם את משתמשת בשדה כזה
            )

            # 🎓 יצירת סטודנט
            education = data.get('education', {})
            Student.objects.create(
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
        course = request.POST.get('course')  # אפשר לשמור אותו בתוך ה-title או description אם אין שדה נפרד
        request_type = 'prerequisite_exemption'
        attachment = request.FILES.get('attachment')

        secretary = User.objects.filter(role='secretary').first()

        full_title = f"({course}) {title}"

        Request.objects.create(
            title=full_title,
            description=description,
            request_type=request_type,
            student=student,
            assigned_to=secretary,
            attachment=attachment if attachment else None
        )

        return redirect('student_request_history')


from django.shortcuts import get_object_or_404

@login_required

def view_request_details_for_other(request, request_id):
    req = get_object_or_404(Request, id=request_id, request_type='other')
    return render(request, 'view_request_details_for_other.html', {'req': req})

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

@login_required
def load_request_form(request):
    request_type = request.GET.get('type')
    allowed_offerings = []

    student = Student.objects.get(user=request.user)
    current_year = int(student.current_year_of_study or student.year_of_study)
    current_sem = student.current_semester or 'A'

    all_offerings = CourseOffering.objects.all()

    if request_type == 'special_exam':
        # הצג את כל הקורסים של שנים קודמות + הסמסטרים שכבר עברו בשנה הנוכחית
        for o in all_offerings:
            if o.year < current_year:
                allowed_offerings.append(o)
            elif o.year == current_year:
                if current_sem == 'A' and o.semester == 'A':
                    allowed_offerings.append(o)
                elif current_sem == 'B':
                    allowed_offerings.append(o)  # גם A וגם B

    elif request_type == 'delay_submission':
        # רק קורסים של השנה הנוכחית, כל הסמסטרים
        for o in all_offerings:
            if o.year == current_year:
                allowed_offerings.append(o)

    elif request_type in ['prerequisite_exemption', 'course_exemption', 'course_unblock', 'registration_exemption']:
        allowed_offerings = list(CourseOffering.objects.all())

    elif request_type == 'cancel_hw_percent':
        # רק קורסים של השנה הנוכחית, כל הסמסטרים
        for o in all_offerings:
            if o.year == current_year:
                allowed_offerings.append(o)
    elif request_type == 'include_hw_grade':
        all_offerings = CourseOffering.objects.all()
        for o in all_offerings:
            if o.year == current_year:
                allowed_offerings.append(o)
    elif request_type == 'iron_swords':
        all_offerings = CourseOffering.objects.all()
        for o in all_offerings:
            if o.year == current_year:
                allowed_offerings.append(o)


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
        course_offering_id = request.POST.get('offering_id')
        attachment = request.FILES.get('attachment')

        course_offering = get_object_or_404(CourseOffering, id=course_offering_id)
        secretary = User.objects.filter(role='secretary').first()

        full_title = f"{course_offering.course.name} - {course_offering.instructor.user.get_full_name()} | {title}"

        Request.objects.create(
            title=full_title,
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
        offering_id = request.POST.get('offering_id')
        course_offering = get_object_or_404(CourseOffering, id=offering_id)

        title = request.POST.get('title')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')

        full_title = f"{course_offering.course.name} - {course_offering.instructor.user.get_full_name()} | {title}"
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
        course_name = request.POST.get('course')
        title = request.POST.get('title')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')

        secretary = User.objects.filter(role='secretary').first()
        full_title = f"{course_name} | {title}"

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
        course_name = request.POST.get('course')
        title = request.POST.get('title')
        description = request.POST.get('description')
        attachment = request.FILES.get('attachment')

        secretary = User.objects.filter(role='secretary').first()
        full_title = f"{course_name} | {title}"

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
            request_type='delay_assignment',
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

        if req.request_type != 'other':
            req.status = status
            if status != 'in_progress':
                req.explanation = explanation
            req.save()

            # ✅ Send email to student
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


