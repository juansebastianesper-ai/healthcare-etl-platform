from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from functools import wraps

ALLOWED_ROLES = {
    'dashboard': ['ADMIN', 'ANALISTA', 'MEDICO'],
    'pacientes': ['ADMIN', 'ANALISTA', 'MEDICO'],
    'etl-page': ['ADMIN', 'ANALISTA'],
    'analytics': ['ADMIN', 'ANALISTA', 'MEDICO'],
    'predictions': ['ADMIN', 'ANALISTA'],
    'reports': ['ADMIN', 'MEDICO'],
    'profile': ['ADMIN', 'ANALISTA', 'MEDICO'],
}


def role_required(view_name):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            allowed = ALLOWED_ROLES.get(view_name, [])
            if request.user.role not in allowed:
                return render(request, '403.html', status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


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


@role_required('dashboard')
def dashboard_view(request):
    return render(request, 'dashboard.html')


@role_required('pacientes')
def pacientes_view(request):
    return render(request, 'pacientes.html')


@role_required('etl-page')
def etl_view(request):
    return render(request, 'etl.html')


@role_required('analytics')
def analytics_view(request):
    return render(request, 'analytics.html')


@role_required('predictions')
def predictions_view(request):
    return render(request, 'predictions.html')


@role_required('profile')
def profile_view(request):
    return render(request, 'profile.html')


@role_required('reports')
def reports_view(request):
    return render(request, 'reports.html')
