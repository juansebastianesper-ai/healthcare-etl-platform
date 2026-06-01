from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'pacientes', views.PatientViewSet, basename='patient')
router.register(r'runs', views.ETLRunViewSet, basename='etl-run')
router.register(r'sources', views.ETLSourceViewSet, basename='etl-source')

urlpatterns = [
    path('', include(router.urls)),
]
