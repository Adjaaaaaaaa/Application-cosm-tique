"""
URL configuration for the API app.

This module defines the URL patterns for internal and external API endpoints.
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Health check endpoint
    path('health/', views.health_check_internal, name='health_check'),
    
    # User profile endpoints
    path('user-profile/<int:user_id>/', views.get_user_profile_internal, name='get_user_profile'),
    path('user/profile', views.update_user_profile_internal, name='update_user_profile'),
    
    # AI service endpoints
    path('enhanced-ai/comprehensive-routine/', views.comprehensive_routine_internal, name='comprehensive_routine'),
    path('ai/analyze-product/', views.analyze_product_internal, name='analyze_product'),
    path('ai/general-question/', views.general_question_internal, name='general_question'),
    
    # Ingredient service endpoints
    path('ingredients/info/', views.get_ingredient_info_internal, name='get_ingredient_info'),
]
