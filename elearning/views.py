from django.shortcuts import render, redirect


def home(request):
    if request.user.is_authenticated:
        if request.user.is_instructor:
            return redirect('instructor_dashboard')
        else:
            return redirect('student_dashboard')

    return render(request, 'home.html', {})
