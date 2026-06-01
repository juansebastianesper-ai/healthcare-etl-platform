from django.urls import path
from django.contrib.auth import views as auth_views
from frontend_views import (
    dashboard_view, pacientes_view, etl_view,
    analytics_view, predictions_view, reports_view,
    login_view, logout_view, profile_view
)

urlpatterns = [
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('pacientes/', pacientes_view, name='pacientes'),
    path('etl/', etl_view, name='etl-page'),
    path('analytics/', analytics_view, name='analytics'),
    path('predictions/', predictions_view, name='predictions'),
    path('reports/', reports_view, name='reports'),
    path('profile/', profile_view, name='profile'),
]
