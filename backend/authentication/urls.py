from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='auth-login'),
    path('register/', views.RegisterView.as_view(), name='auth-register'),
    path('refresh/', views.TokenRefreshView.as_view(), name='auth-refresh'),
    path('profile/', views.ProfileView.as_view(), name='auth-profile'),
    path('users/', views.UserListView.as_view(), name='auth-users'),
]
