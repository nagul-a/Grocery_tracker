"""
Template tags for enhanced authentication features
"""

from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()


@register.inclusion_tag('components/breadcrumb.html')
def breadcrumb(current_page, *args):
    """
    Generate breadcrumb navigation
    
    Usage: {% breadcrumb "Profile Settings" "Dashboard" "dashboard" %}
    """
    breadcrumbs = []
    
    # Always start with Home
    breadcrumbs.append({
        'title': 'Home',
        'url': reverse('home'),
        'active': False
    })
    
    # Add intermediate pages
    for i in range(0, len(args), 2):
        if i + 1 < len(args):
            title = args[i]
            url_name = args[i + 1]
            try:
                url = reverse(url_name)
                breadcrumbs.append({
                    'title': title,
                    'url': url,
                    'active': False
                })
            except:
                # If URL reverse fails, add as text only
                breadcrumbs.append({
                    'title': title,
                    'url': None,
                    'active': False
                })
    
    # Add current page
    breadcrumbs.append({
        'title': current_page,
        'url': None,
        'active': True
    })
    
    return {'breadcrumbs': breadcrumbs}


@register.simple_tag
def profile_completion_percentage(user):
    """
    Calculate profile completion percentage
    """
    if not user.is_authenticated:
        return 0
    
    try:
        profile = user.userprofile
        total_fields = 8
        completed_fields = 0
        
        # Check basic user fields
        if user.first_name:
            completed_fields += 1
        if user.last_name:
            completed_fields += 1
        if user.email:
            completed_fields += 1
        
        # Check profile fields
        if profile.profile_picture:
            completed_fields += 1
        if profile.phone_number:
            completed_fields += 1
        if profile.preferred_theme != 'light':  # Assuming light is default
            completed_fields += 1
        if profile.default_grocery_category != 'Other':  # Assuming Other is default
            completed_fields += 1
        if profile.expiry_reminder_days != 3:  # Assuming 3 is default
            completed_fields += 1
        
        return int((completed_fields / total_fields) * 100)
    except:
        return 0


@register.simple_tag
def profile_completion_items(user):
    """
    Get list of incomplete profile items
    """
    if not user.is_authenticated:
        return []
    
    try:
        profile = user.userprofile
        incomplete_items = []
        
        if not user.first_name:
            incomplete_items.append('First Name')
        if not user.last_name:
            incomplete_items.append('Last Name')
        if not profile.profile_picture:
            incomplete_items.append('Profile Picture')
        if not profile.phone_number:
            incomplete_items.append('Phone Number')
        
        return incomplete_items
    except:
        return []


@register.filter
def user_initials(user):
    """
    Get user initials for avatar placeholder
    """
    if user.first_name and user.last_name:
        return f"{user.first_name[0]}{user.last_name[0]}".upper()
    elif user.first_name:
        return user.first_name[0].upper()
    elif user.username:
        return user.username[0].upper()
    return "U"


@register.simple_tag
def session_info(request):
    """
    Get session information for display
    """
    if not request.user.is_authenticated:
        return {}
    
    session_data = {
        'session_key': request.session.session_key[:8] + '...' if request.session.session_key else 'N/A',
        'expires_at': request.session.get_expiry_date(),
        'is_persistent': not request.session.get_expire_at_browser_close(),
    }
    
    return session_data
