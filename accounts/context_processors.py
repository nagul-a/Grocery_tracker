"""
Context Processors for Smart Grocery Tracker

This module provides context processors that add user-specific data
to all template contexts automatically.
"""

import logging
from .models import MongoDBUserManager

logger = logging.getLogger('grocery_app')


def user_context(request):
    """
    Add user-specific context data to all templates
    """
    context = {}
    
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            # Get user profile
            profile = getattr(request.user, 'userprofile', None)
            
            if profile:
                context.update({
                    'user_profile': profile,
                    'user_theme': profile.preferred_theme,
                    'user_full_name': profile.full_name,
                })
            
            # Get user statistics for navbar
            mongo_manager = MongoDBUserManager()
            user_stats = mongo_manager.get_user_data_stats(str(request.user.id))
            
            # Get quick stats for navbar badges
            from grocery_app.django_models import GroceryItemManager
            
            # For now, get all items (will be filtered by user later)
            all_items = GroceryItemManager.get_all()
            expiring_items = GroceryItemManager.get_expiring_items(days=3)
            low_stock_items = GroceryItemManager.get_low_stock_items(threshold=5)
            
            context.update({
                'expiring_count': len(expiring_items),
                'low_stock_count': len(low_stock_items),
                'total_items_count': len(all_items),
            })
            
        except Exception as e:
            logger.error(f"Error in user context processor: {e}")
            # Provide default values
            context.update({
                'user_theme': 'light',
                'expiring_count': 0,
                'low_stock_count': 0,
                'total_items_count': 0,
            })
    else:
        # Default context for anonymous users
        context.update({
            'user_theme': 'light',
            'expiring_count': 0,
            'low_stock_count': 0,
            'total_items_count': 0,
        })
    
    return context


def app_context(request):
    """
    Add application-wide context data
    """
    return {
        'app_name': 'Smart Grocery Tracker',
        'app_version': '1.0.0',
        'support_email': 'support@smartgrocery.com',
    }
