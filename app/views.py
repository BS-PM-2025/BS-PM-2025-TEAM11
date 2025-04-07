from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
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

def secretary_dashboard(request):
    return render(request, 'secretary_dashboard.html')

def academic_dashboard(request):
    return render(request, 'academic_dashboard.html')
