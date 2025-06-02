"""
Authentication Views for Smart Grocery Tracker

This module contains all authentication-related views including login, registration,
profile management, and user dashboard functionality.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from datetime import timedelta
import json
import logging

from .models import UserProfile, MongoDBUserManager, UserActivityLog, EssentialSettings
from .forms import (
    UserRegistrationForm, UserProfileForm, LoginForm, PasswordChangeForm,
    EssentialSettingsForm, UserUpdateForm, ComprehensiveProfileForm
)

logger = logging.getLogger('grocery_app')


def login_view(request):
    """
    User login view with remember me functionality
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set session expiry based on remember me
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser session
                
                # Log the activity
                UserActivityLog.objects.create(
                    user=user,
                    action='login',
                    description='User logged in',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                # Redirect to next page or dashboard
                next_page = request.GET.get('next', 'dashboard')
                return redirect(next_page)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """
    User registration view
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create user
                user = form.save()
                
                # Create MongoDB collections for user
                mongo_manager = MongoDBUserManager()
                mongo_manager.create_user_collections(str(user.id))
                
                # Log the activity
                UserActivityLog.objects.create(
                    user=user,
                    action='register',
                    description='User registered',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, 'Registration successful! You can now log in.')
                return redirect('login')
                
            except Exception as e:
                logger.error(f"Registration error: {e}")
                messages.error(request, 'Registration failed. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    """
    Enhanced user logout view with session cleanup
    """
    user_name = request.user.first_name or request.user.username

    # Log the activity
    UserActivityLog.objects.create(
        user=request.user,
        action='logout',
        description='User logged out',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        metadata={
            'session_key': request.session.session_key,
            'logout_method': 'manual'
        }
    )

    # Clear session data
    request.session.flush()

    # Logout user
    logout(request)

    messages.success(request, f'Goodbye {user_name}! You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """
    Comprehensive user profile management view with statistics and settings summary
    """
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    # Get user statistics from profile model
    user_stats = profile.get_user_statistics()

    # Get essential settings
    try:
        essential_settings = request.user.essentialsettings
    except EssentialSettings.DoesNotExist:
        essential_settings = EssentialSettings.objects.create(user=request.user)

    # Get recent activity
    recent_activities = UserActivityLog.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:5]

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            # Log the activity
            UserActivityLog.objects.create(
                user=request.user,
                action='profile_updated',
                description='Profile information updated',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={
                    'updated_fields': list(user_form.changed_data) + list(profile_form.changed_data)
                }
            )

            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
        'user_stats': user_stats,
        'essential_settings': essential_settings,
        'recent_activities': recent_activities,
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def user_dashboard(request):
    """
    Enhanced user dashboard with personalized statistics
    """
    try:
        # Get user profile
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    # Get MongoDB statistics
    mongo_manager = MongoDBUserManager()
    user_stats = mongo_manager.get_user_data_stats(str(request.user.id))
    
    # Get recent activities
    recent_activities = UserActivityLog.objects.filter(
        user=request.user
    ).exclude(
        action__in=['login', 'logout']
    ).order_by('-timestamp')[:10]
    
    # Get user-specific grocery data (this will be enhanced with MongoDB integration)
    from grocery_app.django_models import GroceryItemManager
    
    # For now, get all items (will be filtered by user later)
    all_items = GroceryItemManager.get_all()
    expiring_items = GroceryItemManager.get_expiring_items(days=profile.expiry_reminder_days)
    low_stock_items = GroceryItemManager.get_low_stock_items(threshold=5)
    
    # Calculate user-specific statistics using improved calculation
    from grocery_app.utils import calculate_inventory_statistics
    inventory_stats = calculate_inventory_statistics(all_items)

    dashboard_stats = {
        'total_items': len(all_items),
        'expiring_soon': len(expiring_items),
        'low_stock': len(low_stock_items),
        'total_value': inventory_stats['active_value'],  # Only count active inventory
        'categories_count': len(set(item.get('category') for item in all_items)),
    }
    
    context = {
        'profile': profile,
        'user_stats': user_stats,
        'dashboard_stats': dashboard_stats,
        'recent_activities': recent_activities,
        'expiring_items': expiring_items[:5],  # Show top 5
        'low_stock_items': low_stock_items[:5],  # Show top 5
    }
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_theme_preference(request):
    """
    AJAX endpoint to update user's theme preference
    """
    try:
        data = json.loads(request.body)
        theme = data.get('theme')
        
        if theme in ['light', 'dark', 'auto']:
            profile = request.user.userprofile
            profile.preferred_theme = theme
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Theme preference updated',
                'theme': theme
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid theme selection'
            })
            
    except Exception as e:
        logger.error(f"Error updating theme preference: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to update theme preference'
        })


@login_required
def user_activity_log(request):
    """
    View user activity history
    """
    activities = UserActivityLog.objects.filter(
        user=request.user
    ).order_by('-timestamp')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(activities, 25)  # Show 25 activities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'activities': page_obj,
    }
    
    return render(request, 'accounts/activity_log.html', context)


@login_required
def password_change_view(request):
    """
    Password change view with enhanced security
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()

            # Log the activity
            UserActivityLog.objects.create(
                user=request.user,
                action='password_changed',
                description='User changed password',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'change_method': 'profile_settings'}
            )

            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form,
    }

    return render(request, 'accounts/password_change.html', context)


@login_required
def session_extend_view(request):
    """
    AJAX endpoint to extend user session
    """
    if request.method == 'POST':
        try:
            # Extend session by resetting expiry
            request.session.set_expiry(1800)  # 30 minutes

            # Log the activity
            UserActivityLog.objects.create(
                user=request.user,
                action='session_extended',
                description='User extended session',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'extension_time': 1800}
            )

            return JsonResponse({
                'success': True,
                'message': 'Session extended successfully',
                'expires_in': 1800
            })

        except Exception as e:
            logger.error(f"Error extending session: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Failed to extend session'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Password reset views (using Django's built-in views with custom templates)
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = '/accounts/password-reset/done/'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = '/accounts/password-reset/complete/'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


# ===== ESSENTIAL SETTINGS VIEW =====

@login_required
def essential_settings(request):
    """
    Simplified essential settings page
    """
    try:
        settings = request.user.essentialsettings
    except EssentialSettings.DoesNotExist:
        settings = EssentialSettings.objects.create(user=request.user)

    if request.method == 'POST':
        form = EssentialSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()

            # Log the activity
            UserActivityLog.objects.create(
                user=request.user,
                action='settings_updated',
                description='Essential settings updated',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'settings_type': 'essential'}
            )

            messages.success(request, 'Settings updated successfully!')
            return redirect('accounts:essential_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EssentialSettingsForm(instance=settings)

    # Get recent settings changes
    recent_activities = UserActivityLog.objects.filter(
        user=request.user,
        action='settings_updated'
    ).order_by('-timestamp')[:3]

    context = {
        'form': form,
        'settings': settings,
        'recent_activities': recent_activities,
    }

    return render(request, 'accounts/settings/essential.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def quick_theme_update(request):
    """
    AJAX endpoint for quick theme updates
    """
    try:
        data = json.loads(request.body)
        theme = data.get('theme')

        if theme not in ['light', 'dark']:
            return JsonResponse({
                'success': False,
                'message': 'Invalid theme value'
            })

        settings, created = EssentialSettings.objects.get_or_create(user=request.user)
        settings.theme = theme
        settings.save()

        return JsonResponse({
            'success': True,
            'message': f'Theme changed to {theme}',
            'theme': theme
        })

    except Exception as e:
        logger.error(f"Error updating theme: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to update theme'
        })


# Legacy view redirects for backward compatibility
@login_required
def settings_dashboard(request):
    """Redirect to essential settings"""
    return redirect('accounts:essential_settings')


@login_required
def appearance_settings(request):
    """Redirect to essential settings"""
    return redirect('accounts:essential_settings')


# Legacy redirects for backward compatibility
@login_required
def notification_settings(request):
    """Redirect to essential settings"""
    return redirect('accounts:essential_settings')


@login_required
def grocery_settings(request):
    """Redirect to essential settings"""
    return redirect('accounts:essential_settings')


@login_required
def privacy_settings(request):
    """Redirect to essential settings"""
    return redirect('accounts:essential_settings')

@login_required
def security_settings(request):
    """Redirect to essential settings"""
    return redirect('accounts:essential_settings')

@login_required
def backup_settings(request):
    """Redirect to essential settings"""
    return redirect('accounts:essential_settings')

@login_required
def language_settings(request):
    """Redirect to essential settings"""
    return redirect('accounts:essential_settings')

@login_required
def advanced_settings(request):
    """Redirect to essential settings"""
    return redirect('accounts:essential_settings')


# ===== COMPREHENSIVE PROFILE VIEW =====

@login_required
def comprehensive_profile(request):
    """
    Comprehensive user profile page with all features
    """
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ComprehensiveProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user
        )

        if form.is_valid():
            form.save()

            # Log the activity
            UserActivityLog.objects.create(
                user=request.user,
                action='profile_updated',
                description='Profile information updated',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'profile_fields_updated': list(form.changed_data)}
            )

            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:comprehensive_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ComprehensiveProfileForm(instance=profile, user=request.user)

    # Get user statistics
    user_stats = profile.get_user_statistics()

    # Get account settings summary
    settings_summary = profile.get_account_settings_summary()

    # Get recent activity
    recent_activities = UserActivityLog.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:5]

    context = {
        'form': form,
        'profile': profile,
        'user_stats': user_stats,
        'settings_summary': settings_summary,
        'recent_activities': recent_activities,
    }

    return render(request, 'accounts/profile/comprehensive.html', context)
