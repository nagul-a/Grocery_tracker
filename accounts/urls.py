"""
URL Configuration for Accounts App

This module defines URL patterns for authentication and user management views.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile Management URLs
    path('profile/', views.comprehensive_profile, name='profile'),
    path('profile/comprehensive/', views.comprehensive_profile, name='comprehensive_profile'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('activity/', views.user_activity_log, name='activity_log'),
    
    # Security & Settings
    path('password-change/', views.password_change_view, name='password_change'),

    # ===== ESSENTIAL SETTINGS URLS =====
    path('settings/', views.essential_settings, name='essential_settings'),
    path('settings/dashboard/', views.settings_dashboard, name='settings_dashboard'),

    # Legacy redirects for backward compatibility
    path('settings/appearance/', views.appearance_settings, name='appearance_settings'),
    path('settings/notifications/', views.notification_settings, name='notification_settings'),
    path('settings/grocery/', views.grocery_settings, name='grocery_settings'),
    path('settings/privacy/', views.privacy_settings, name='privacy_settings'),
    path('settings/security/', views.security_settings, name='security_settings'),
    path('settings/backup/', views.backup_settings, name='backup_settings'),
    path('settings/language/', views.language_settings, name='language_settings'),
    path('settings/advanced/', views.advanced_settings, name='advanced_settings'),

    # AJAX Endpoints
    path('api/update-theme/', views.update_theme_preference, name='update_theme'),
    path('api/extend-session/', views.session_extend_view, name='extend_session'),
    path('api/quick-theme/', views.quick_theme_update, name='quick_theme_update'),
    
    # Password Reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
