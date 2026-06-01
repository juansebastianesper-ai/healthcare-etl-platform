from django.urls import path
from . import views

urlpatterns = [
    path('kpis/', views.kpis_view, name='analytics-kpis'),
    path('estadisticas/', views.estadisticas_view, name='analytics-estadisticas'),
    path('segmentacion/<str:criterio>/', views.segmentacion_view, name='analytics-segmentacion'),
]
