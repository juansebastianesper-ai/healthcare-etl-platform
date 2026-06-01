from django.urls import path
from . import views

urlpatterns = [
    path('pdf/<str:report_type>/', views.report_pdf, name='report-pdf'),
    path('pdf/', views.report_pdf, name='report-pdf-default'),
    path('csv/<str:report_type>/', views.report_csv, name='report-csv'),
    path('excel/<str:report_type>/', views.report_excel, name='report-excel'),
]
