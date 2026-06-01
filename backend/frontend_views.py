from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        return render(request, 'login.html', {'error': 'Credenciales inválidas'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')


@login_required
def pacientes_view(request):
    return render(request, 'pacientes.html')


@login_required
def etl_view(request):
    return render(request, 'etl.html')


@login_required
def analytics_view(request):
    return render(request, 'analytics.html')


@login_required
def predictions_view(request):
    return render(request, 'predictions.html')


@login_required
def profile_view(request):
    return render(request, 'profile.html')


@login_required
def reports_view(request):
    return render(request, 'reports.html')
