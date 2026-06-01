from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'models', views.MLModelViewSet, basename='ml-model')
router.register(r'predictions', views.PredictionViewSet, basename='prediction')

urlpatterns = [
    path('', include(router.urls)),
]
