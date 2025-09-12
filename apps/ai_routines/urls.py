"""
URLs for AI Routines app - Integrated API
"""

from django.urls import path
from . import views

app_name = 'ai_routines'

urlpatterns = [
    # Vues principales
    path('', views.ai_routines_view, name='ai_routines'),
    path('beauty-assistant/', views.beauty_assistant_view, name='beauty_assistant'),
    path('product-analysis/', views.product_analysis_view, name='product_analysis'),
    path('routine-history/', views.routine_history_view, name='routine_history'),
    path('routine-detail/<int:routine_id>/', views.routine_detail_view, name='routine_detail'),
    path('user-profile/', views.user_profile_view, name='user_profile'),
    
    # Endpoints API
    path('api/beauty-assistant/', views.api_beauty_assistant, name='api_beauty_assistant'),
]
