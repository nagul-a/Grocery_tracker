"""
User Authentication Middleware for Smart Grocery Tracker

This middleware handles user-specific data filtering and session management.
"""

import logging
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from .models import UserActivityLog

logger = logging.getLogger('grocery_app')


class UserDataFilterMiddleware:
    """
    Middleware to ensure user-specific data filtering and logging
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process request before view
        self.process_request(request)
        
        # Get response from view
        response = self.get_response(request)
        
        # Process response after view
        return self.process_response(request, response)
    
    def process_request(self, request):
        """
        Process incoming request
        """
        # Add user_id to request for easy access
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.user_id = str(request.user.id)
        else:
            request.user_id = None
        
        # Log page visits for authenticated users
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            request.method == 'GET' and
            not request.path.startswith('/static/') and
            not request.path.startswith('/media/') and
            not request.path.startswith('/api/')):
            
            try:
                # Don't log every single page visit, just important ones
                important_paths = [
                    '/dashboard/',
                    '/accounts/profile/',
                    '/add/',
                    '/analytics/',
                    '/smart-suggestions/',
                    '/meal-planner/',
                    '/price-comparison/'
                ]
                
                if any(request.path.startswith(path) for path in important_paths):
                    UserActivityLog.objects.create(
                        user=request.user,
                        action='page_visit',
                        description=f'Visited {request.path}',
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        metadata={'path': request.path}
                    )
            except Exception as e:
                logger.error(f"Error logging user activity: {e}")
    
    def process_response(self, request, response):
        """
        Process outgoing response
        """
        # Add user theme preference to response context
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            hasattr(request.user, 'userprofile')):
            
            try:
                theme = request.user.userprofile.preferred_theme
                # Add theme to response headers for JavaScript access
                response['X-User-Theme'] = theme
            except Exception as e:
                logger.error(f"Error setting user theme: {e}")
        
        return response
    
    def get_client_ip(self, request):
        """
        Get client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ThemeMiddleware:
    """
    Middleware to handle user theme preferences
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Set theme context for templates
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                profile = request.user.userprofile
                request.user_theme = profile.preferred_theme
            except:
                request.user_theme = 'light'
        else:
            request.user_theme = 'light'
        
        response = self.get_response(request)
        return response


class SecurityMiddleware:
    """
    Additional security middleware for user data protection
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add security headers
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Add user-specific cache control
        if hasattr(request, 'user') and request.user.is_authenticated:
            response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
