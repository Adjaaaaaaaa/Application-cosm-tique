"""
URL patterns for the accounts app.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/verify/', views.verify_email_view, name='signup_verify'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('allergies/add/', views.add_allergy_view, name='add_allergy'),
    path('allergies/<int:allergy_id>/delete/', views.delete_allergy_view, name='delete_allergy'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),

]
