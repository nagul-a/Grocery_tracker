"""
MongoDB-based Views for Smart Grocery Tracker

This module contains views that use MongoDB for data storage instead of Django ORM.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json
import logging
from bson import ObjectId

from .models import GroceryItem as MongoGroceryItem, AnalyticsModel

logger = logging.getLogger('grocery_app')

@login_required
def grocery_list_mongodb(request):
    """Display grocery list using MongoDB"""
    try:
        grocery_model = MongoGroceryItem()
        
        # Get filter parameters
        category_filter = request.GET.get('category', '')
        search_query = request.GET.get('search', '')
        
        # Build filters
        filters = {}
        if category_filter:
            filters['category'] = category_filter
        if search_query:
            filters['search'] = search_query
        
        # Get user ID (convert to string for MongoDB)
        user_id = str(request.user.id)
        
        # Get all items for the user
        items = grocery_model.get_all(user_id=user_id, filters=filters)
        
        # Get categories for filter dropdown
        categories = MongoGroceryItem.CATEGORIES
        
        # Get category statistics
        analytics_model = AnalyticsModel()
        category_stats = analytics_model.get_categories_stats(user_id=user_id)
        
        # Get expiring items (next 7 days)
        expiring_items = grocery_model.get_expiring_items(days=7, user_id=user_id)
        
        # Get low stock items
        low_stock_items = grocery_model.get_low_stock_items(threshold=5, user_id=user_id)
        
        context = {
            'items': items,
            'categories': categories,
            'category_stats': category_stats,
            'expiring_items': expiring_items,
            'low_stock_items': low_stock_items,
            'selected_category': category_filter,
            'search_query': search_query,
            'total_items': len(items),
            'using_mongodb': True,  # Flag to indicate MongoDB usage
        }
        
        return render(request, 'grocery_app/grocery_list.html', context)
        
    except Exception as e:
        logger.error(f"Error in grocery_list_mongodb: {e}")
        messages.error(request, f"Error loading grocery list: {str(e)}")
        return render(request, 'grocery_app/grocery_list.html', {'items': [], 'using_mongodb': True})

@login_required
def add_item_mongodb(request):
    """Add new grocery item to MongoDB - handles both GET and POST"""
    if request.method == 'GET':
        # Show add item form
        categories = MongoGroceryItem.CATEGORIES
        units = MongoGroceryItem.UNITS
        context = {
            'categories': categories,
            'units': units,
            'using_mongodb': True,
        }
        return render(request, 'grocery_app/add_item.html', context)

    elif request.method == 'POST':
        # Add new grocery item to MongoDB
        try:
            grocery_model = MongoGroceryItem()

            # Get form data
            item_data = {
                'name': request.POST.get('name', '').strip(),
                'category': request.POST.get('category', ''),
                'quantity': int(request.POST.get('quantity', 1)),
                'unit': request.POST.get('unit', 'pieces'),
                'price': float(request.POST.get('price', 0)) if request.POST.get('price') else None,
                'notes': request.POST.get('notes', '').strip(),
                'user_id': str(request.user.id),
            }
        
            # Handle optional dates
            expiry_date = request.POST.get('expiry_date')
            if expiry_date:
                item_data['expiry_date'] = datetime.fromisoformat(expiry_date)

            last_purchased = request.POST.get('last_purchased')
            if last_purchased:
                item_data['last_purchased'] = datetime.fromisoformat(last_purchased)
            else:
                item_data['last_purchased'] = datetime.now()

            # Validate required fields
            if not item_data['name']:
                messages.error(request, "Item name is required.")
                return redirect('grocery_list_mongodb')

            if not item_data['category']:
                messages.error(request, "Category is required.")
                return redirect('grocery_list_mongodb')

            # Create item in MongoDB
            item_id = grocery_model.create(item_data)

            if item_id:
                messages.success(request, f"✅ Added '{item_data['name']}' to your grocery list!")
                logger.info(f"User {request.user.username} added item: {item_data['name']} (MongoDB ID: {item_id})")
            else:
                messages.error(request, "Failed to add item. Please try again.")

            return redirect('grocery_list_mongodb')

        except ValueError as e:
            messages.error(request, f"Invalid data: {str(e)}")
            return redirect('grocery_list_mongodb')
        except Exception as e:
            logger.error(f"Error adding item to MongoDB: {e}")
            messages.error(request, f"Error adding item: {str(e)}")
            return redirect('grocery_list_mongodb')

@login_required
@require_http_methods(["POST"])
def update_item_mongodb(request, item_id):
    """Update grocery item in MongoDB"""
    try:
        grocery_model = MongoGroceryItem()
        
        # Get the existing item to verify ownership
        existing_item = grocery_model.get_by_id(item_id)
        if not existing_item or existing_item.get('user_id') != str(request.user.id):
            messages.error(request, "Item not found or access denied.")
            return redirect('grocery_app:grocery_list_mongodb')
        
        # Get update data
        update_data = {}
        
        if 'name' in request.POST:
            update_data['name'] = request.POST.get('name', '').strip()
        if 'category' in request.POST:
            update_data['category'] = request.POST.get('category', '')
        if 'quantity' in request.POST:
            update_data['quantity'] = int(request.POST.get('quantity', 1))
        if 'unit' in request.POST:
            update_data['unit'] = request.POST.get('unit', 'pieces')
        if 'price' in request.POST:
            price_str = request.POST.get('price', '')
            update_data['price'] = float(price_str) if price_str else None
        if 'notes' in request.POST:
            update_data['notes'] = request.POST.get('notes', '').strip()
        
        # Handle optional dates
        if 'expiry_date' in request.POST:
            expiry_date = request.POST.get('expiry_date')
            update_data['expiry_date'] = datetime.fromisoformat(expiry_date) if expiry_date else None
        
        if 'last_purchased' in request.POST:
            last_purchased = request.POST.get('last_purchased')
            update_data['last_purchased'] = datetime.fromisoformat(last_purchased) if last_purchased else None
        
        # Update item in MongoDB
        success = grocery_model.update(item_id, update_data)
        
        if success:
            messages.success(request, f"✅ Updated '{update_data.get('name', existing_item['name'])}'!")
            logger.info(f"User {request.user.username} updated item: {item_id}")
        else:
            messages.error(request, "Failed to update item. Please try again.")
        
        return redirect('grocery_app:grocery_list_mongodb')
        
    except ValueError as e:
        messages.error(request, f"Invalid data: {str(e)}")
        return redirect('grocery_app:grocery_list_mongodb')
    except Exception as e:
        logger.error(f"Error updating item in MongoDB: {e}")
        messages.error(request, f"Error updating item: {str(e)}")
        return redirect('grocery_app:grocery_list_mongodb')

@login_required
@require_http_methods(["POST"])
def delete_item_mongodb(request, item_id):
    """Delete grocery item from MongoDB"""
    try:
        grocery_model = MongoGroceryItem()
        
        # Get the existing item to verify ownership and get name for message
        existing_item = grocery_model.get_by_id(item_id)
        if not existing_item or existing_item.get('user_id') != str(request.user.id):
            messages.error(request, "Item not found or access denied.")
            return redirect('grocery_app:grocery_list_mongodb')
        
        # Delete item from MongoDB
        success = grocery_model.delete(item_id)
        
        if success:
            messages.success(request, f"🗑️ Deleted '{existing_item['name']}' from your grocery list!")
            logger.info(f"User {request.user.username} deleted item: {item_id}")
        else:
            messages.error(request, "Failed to delete item. Please try again.")
        
        return redirect('grocery_app:grocery_list_mongodb')
        
    except Exception as e:
        logger.error(f"Error deleting item from MongoDB: {e}")
        messages.error(request, f"Error deleting item: {str(e)}")
        return redirect('grocery_app:grocery_list_mongodb')

@login_required
def get_item_mongodb(request, item_id):
    """Get single item data for AJAX requests"""
    try:
        grocery_model = MongoGroceryItem()
        
        # Get item
        item = grocery_model.get_by_id(item_id)
        if not item or item.get('user_id') != str(request.user.id):
            return JsonResponse({'error': 'Item not found or access denied'}, status=404)
        
        # Convert datetime objects to strings for JSON serialization
        if item.get('expiry_date'):
            item['expiry_date'] = item['expiry_date'].isoformat()
        if item.get('last_purchased'):
            item['last_purchased'] = item['last_purchased'].isoformat()
        if item.get('created_at'):
            item['created_at'] = item['created_at'].isoformat()
        if item.get('updated_at'):
            item['updated_at'] = item['updated_at'].isoformat()
        
        return JsonResponse({'item': item})
        
    except Exception as e:
        logger.error(f"Error getting item from MongoDB: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def search_items_mongodb(request):
    """Search items in MongoDB"""
    try:
        search_term = request.GET.get('q', '').strip()
        if not search_term:
            return JsonResponse({'items': []})
        
        grocery_model = MongoGroceryItem()
        user_id = str(request.user.id)
        
        # Search items
        items = grocery_model.search_items(search_term, user_id=user_id)
        
        # Convert datetime objects to strings for JSON serialization
        for item in items:
            if item.get('expiry_date'):
                item['expiry_date'] = item['expiry_date'].isoformat()
            if item.get('last_purchased'):
                item['last_purchased'] = item['last_purchased'].isoformat()
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
            if item.get('updated_at'):
                item['updated_at'] = item['updated_at'].isoformat()
        
        return JsonResponse({'items': items})
        
    except Exception as e:
        logger.error(f"Error searching items in MongoDB: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def analytics_mongodb(request):
    """Analytics page using MongoDB data"""
    try:
        user_id = str(request.user.id)
        analytics_model = AnalyticsModel()
        
        # Get spending analytics for last 30 days
        spending_data = analytics_model.get_spending_analytics(user_id=user_id, days=30)
        
        # Get category statistics
        category_stats = analytics_model.get_categories_stats(user_id=user_id)
        
        grocery_model = MongoGroceryItem()
        
        # Get expiring items
        expiring_items = grocery_model.get_expiring_items(days=7, user_id=user_id)
        
        # Get low stock items
        low_stock_items = grocery_model.get_low_stock_items(threshold=5, user_id=user_id)
        
        context = {
            'spending_data': spending_data,
            'category_stats': category_stats,
            'expiring_items': expiring_items,
            'low_stock_items': low_stock_items,
            'using_mongodb': True,
        }
        
        return render(request, 'grocery_app/analytics.html', context)
        
    except Exception as e:
        logger.error(f"Error in analytics_mongodb: {e}")
        messages.error(request, f"Error loading analytics: {str(e)}")
        return render(request, 'grocery_app/analytics.html', {'using_mongodb': True})
