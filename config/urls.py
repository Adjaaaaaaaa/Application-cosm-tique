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
from apps.internal_api import (
    get_user_profile_internal, health_check_internal,
    comprehensive_routine_internal, analyze_product_internal,
    get_ingredient_info_internal, general_question_internal
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('beautyscan/', include('apps.scans.urls')),
    path('payments/', include('apps.payments.urls')),
    path('ai-routines/', include('apps.ai_routines.urls')),
    
    
    # API Interne - Accès restreint aux services internes uniquement
    path('internal-api/user-profile/<int:user_id>/', get_user_profile_internal, name='internal_user_profile'),
    path('internal-api/user-profile/<int:user_id>', get_user_profile_internal, name='internal_user_profile_no_slash'),
    path('internal-api/health/', health_check_internal, name='internal_health'),
    path('internal-api/health', health_check_internal, name='internal_health_no_slash'),
    
    # API Interne - Endpoints fonctionnels sécurisés
    path('internal-api/enhanced-ai/comprehensive-routine/', comprehensive_routine_internal, name='internal_comprehensive_routine'),
    path('internal-api/enhanced-ai/comprehensive-routine', comprehensive_routine_internal, name='internal_comprehensive_routine_no_slash'),
    path('internal-api/ai/analyze-product/', analyze_product_internal, name='internal_analyze_product'),
    path('internal-api/ai/analyze-product', analyze_product_internal, name='internal_analyze_product_no_slash'),
    path('internal-api/ingredients/info/', get_ingredient_info_internal, name='internal_ingredient_info'),
    path('internal-api/ingredients/info', get_ingredient_info_internal, name='internal_ingredient_info_no_slash'),
    path('internal-api/ai/general-question/', general_question_internal, name='internal_general_question'),
    path('internal-api/ai/general-question', general_question_internal, name='internal_general_question_no_slash'),
    
    # Documentation API Interne
    path('docs/internal-api/', TemplateView.as_view(template_name='docs/internal_api_docs.html'), name='internal_api_docs'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files from both directories
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
