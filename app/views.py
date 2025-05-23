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


@login_required
@never_cache

@login_required
@never_cache
def student_request_history_view(request):
    try:
        student_profile = Student.objects.get(user=request.user)
        requests = Request.objects.filter(
            student=student_profile,
            status__in=['pending', 'accepted', 'rejected', 'in_progress']
        ).order_by('-submitted_at')
    except Student.DoesNotExist:
        requests = []
    return render(request, 'student_request_history.html', {'requests': requests})



from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from app.models import Request

@login_required
@never_cache
def secretary_requests_api(request):
    user = request.user

    requests = Request.objects.filter(
        assigned_to=user,
        status='pending'
    ).exclude(request_type='other')  # ✅ exclude "other" requests

    data = [
        {
            'id': r.id,
            'title': r.title,
            'description': r.description,
            'status': r.status,
            'submitted_at': r.submitted_at,
            'request_type': r.request_type,
            'assigned_to': r.assigned_to.id,
            'secretary_id': user.id
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
    allowed_offerings = []

    student = Student.objects.get(user=request.user)
    today = date.today()
    year = today.year
    month = today.month

    if month >= 10:  # אוקטובר, נובמבר, דצמבר – תחילת שנה אקדמית
        current_year = f"{year}-{year + 1}"
    else:  # ינואר עד ספטמבר – עדיין בתוך השנה שהתחילה באוקטובר של השנה הקודמת
        current_year = f"{year - 1}-{year}"
    current_sem = student.current_semester or 'A'

    all_enrollments = StudentCourseEnrollment.objects.filter(student=student)
    all_offerings = CourseOffering.objects.filter(
        course__in=[e.course for e in all_enrollments],
        year__in=[e.academic_year for e in all_enrollments],
        semester__in=[e.semester for e in all_enrollments]
    )

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
