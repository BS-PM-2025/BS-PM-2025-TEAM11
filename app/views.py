from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Request
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


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


def student_dashboard(request):
    return render(request, 'student_dashboard.html')

@login_required
def secretary_dashboard(request):
    if request.user.role != 'secretary':
        return redirect('login')

    return render(request, 'secretary_dashboard.html')

@login_required
def academic_dashboard(request):
    if request.user.role != 'academic':
        return redirect('login')
    return render(request, 'academic_dashboard.html')
def academic_request_history_view(request):
    return render(request, 'academic_request_history.html')
def secretary_request_history_view(request):
    return render(request, 'secretary_request_history.html')


@login_required
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
def secretary_requests_api(request):
    user = request.user
    status = request.GET.get('status', None)

    if status:
        requests = Request.objects.filter(assigned_to=user, status=status)
    else:
        requests = Request.objects.filter(assigned_to=user)

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

