"""
URL configuration for BeautyScan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from apps.api_views import health_check, comprehensive_routine, analyze_product, get_ingredient_info, general_question
from apps.internal_api import get_user_profile_internal, health_check_internal

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('beautyscan/', include('apps.scans.urls')),
    path('payments/', include('apps.payments.urls')),
    path('ai-routines/', include('apps.ai_routines.urls')),
    
    # API Endpoints
    path('api/v1/health/', health_check, name='api_health'),
    path('api/v1/health', health_check, name='api_health_no_slash'),
    path('api/v1/enhanced-ai/comprehensive-routine/', comprehensive_routine, name='api_comprehensive_routine'),
    path('api/v1/enhanced-ai/comprehensive-routine', comprehensive_routine, name='api_comprehensive_routine_no_slash'),
    path('api/v1/ai/analyze-product/', analyze_product, name='api_analyze_product'),
    path('api/v1/ai/analyze-product', analyze_product, name='api_analyze_product_no_slash'),
    path('api/v1/ingredients/info/', get_ingredient_info, name='api_ingredient_info'),
    path('api/v1/ingredients/info', get_ingredient_info, name='api_ingredient_info_no_slash'),
    path('api/v1/ai/general-question/', general_question, name='api_general_question'),
    path('api/v1/ai/general-question', general_question, name='api_general_question_no_slash'),
    
    # API Interne - Accès restreint aux services internes uniquement
    path('internal-api/user-profile/<int:user_id>/', get_user_profile_internal, name='internal_user_profile'),
    path('internal-api/user-profile/<int:user_id>', get_user_profile_internal, name='internal_user_profile_no_slash'),
    path('internal-api/health/', health_check_internal, name='internal_health'),
    path('internal-api/health', health_check_internal, name='internal_health_no_slash'),
    
    # Documentation API Interne
    path('docs/internal-api/', TemplateView.as_view(template_name='docs/internal_api_docs.html'), name='internal_api_docs'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files from both directories
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
