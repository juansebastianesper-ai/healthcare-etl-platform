from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Healthcare ETL Platform API",
        default_version='v1',
        description="API de la Plataforma Inteligente de Analítica Clínica",
        terms_of_service="https://www.healthcare-etl.com/terms/",
        contact=openapi.Contact(email="admin@healthcare-etl.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

favicon_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#0d6efd"/><text x="16" y="23" text-anchor="middle" font-size="20" font-weight="bold" fill="white" font-family="Arial">H</text></svg>'

urlpatterns = [
    path('favicon.ico', lambda r: HttpResponse(favicon_svg, content_type='image/svg+xml')),
    path('api/health/', lambda r: JsonResponse({'status': 'ok'}), name='health-check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/etl/', include('etl.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/ml/', include('ml.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/reports/', include('reports.urls')),
    path('', include('config.frontend_urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
