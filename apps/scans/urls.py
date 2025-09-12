"""
URLs for scans app.
"""

from django.urls import path
from . import views

app_name = 'scans'

urlpatterns = [
    path('', views.scan_dashboard, name='dashboard'),
    path('demo/', views.demo_scan_view, name='demo_scan'),
    path('list/', views.ScanListView.as_view(), name='scan_list'),
    path('create/', views.ScanCreateView.as_view(), name='scan_create'),
    path('<int:pk>/', views.ScanDetailView.as_view(), name='scan_detail'),
    path('<int:scan_id>/analysis/', views.scan_analysis, name='scan_analysis'),
    path('<int:scan_id>/delete/', views.delete_scan, name='delete_scan'),
    path('api/create/', views.ScanAPIView.as_view(), name='scan_api_create'),
    # Page À propos de nous
    path('about/', views.about_view, name='about'),
]
