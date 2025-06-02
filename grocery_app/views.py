"""
Views for Smart Grocery Tracker

This module contains all the function-based views for the grocery tracking application.
Includes CRUD operations, AI-powered features, and analytics.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from .django_models import GroceryItemManager, AnalyticsModel
from .ai_features import SmartSuggestions, MealPlanner
from .utils import format_date, calculate_days_until_expiry

logger = logging.getLogger('grocery_app')


@login_required
def home(request):
    """
    Homepage - Display grocery list with search and filter options
    """
    try:
        # Using GroceryItemManager for database operations

        # Get filter parameters
        search_query = request.GET.get('search', '')
        category_filter = request.GET.get('category', '')
        show_expiring = request.GET.get('expiring', False)

        # Build filters
        filters = {}
        if search_query:
            filters['search'] = search_query
        if category_filter:
            filters['category'] = category_filter
        if show_expiring:
            filters['expiring_soon'] = True

        # Get grocery items with optimized queries

        if search_query:
            items = GroceryItemManager.search_items(search_query)
            if category_filter:
                items = [item for item in items if item.get('category') == category_filter]
        else:
            items = GroceryItemManager.get_all(filters=filters)

        # Get categories for filter dropdown
        from .django_models import GroceryItem
        categories = [choice[1] for choice in GroceryItem.CATEGORY_CHOICES]  # Import added in function

        # Get category statistics
        category_stats = GroceryItemManager.get_categories_stats()

        # Get expiring items count
        expiring_items = GroceryItemManager.get_expiring_items(days=7)
        expiring_count = len(expiring_items)

        # Get low stock items
        low_stock_items = GroceryItemManager.get_low_stock_items(threshold=5)
        low_stock_count = len(low_stock_items)

        # Pagination
        paginator = Paginator(items, 12)  # Show 12 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'items': page_obj,
            'categories': categories,
            'category_stats': category_stats,
            'search_query': search_query,
            'category_filter': category_filter,
            'show_expiring': show_expiring,
            'expiring_count': expiring_count,
            'low_stock_count': low_stock_count,
            'total_items': len(items)
        }

        return render(request, 'grocery_app/home.html', context)

    except Exception as e:
        logger.error(f"Error in home view: {e}")
        messages.error(request, "An error occurred while loading the grocery list.")
        return render(request, 'grocery_app/home.html', {'items': [], 'categories': []})


@login_required
def add_item(request):
    """
    Add new grocery item
    """
    if request.method == 'POST':
        try:
            # Using GroceryItemManager

            # Extract form data
            item_data = {
                'name': request.POST.get('name', '').strip(),
                'category': request.POST.get('category', ''),
                'quantity': int(request.POST.get('quantity', 1)),
                'unit': request.POST.get('unit', ''),
                'price': float(request.POST.get('price', 0)) if request.POST.get('price') else None,
                'notes': request.POST.get('notes', '').strip(),
                'brand': request.POST.get('brand', '').strip(),
                'store': request.POST.get('store', '').strip(),
            }

            # Handle optional dates
            expiry_date = request.POST.get('expiry_date')
            if expiry_date:
                item_data['expiry_date'] = expiry_date

            last_purchased = request.POST.get('last_purchased')
            if last_purchased:
                item_data['last_purchased'] = last_purchased

            # Create item
            item_id = GroceryItemManager.create(item_data)

            messages.success(request, f"Successfully added {item_data['name']} to your grocery list!")
            logger.info(f"Added new grocery item: {item_data['name']}")

            return redirect('home')

        except ValueError as e:
            messages.error(request, f"Invalid data: {str(e)}")
        except Exception as e:
            logger.error(f"Error adding grocery item: {e}")
            messages.error(request, "An error occurred while adding the item.")

    # GET request - show form
    # Using GroceryItemManager
    from .django_models import GroceryItem
    context = {
        'categories': [choice[1] for choice in GroceryItem.CATEGORY_CHOICES],
        'units': [choice[1] for choice in GroceryItem.UNIT_CHOICES],
    }

    return render(request, 'grocery_app/add_item.html', context)


@login_required
def edit_item(request, item_id):
    """
    Edit existing grocery item
    """
    # Using GroceryItemManager

    # Get the item
    item = GroceryItemManager.get_by_id(item_id)
    if not item:
        messages.error(request, "Item not found.")
        return redirect('home')

    if request.method == 'POST':
        try:
            # Extract form data
            update_data = {
                'name': request.POST.get('name', '').strip(),
                'category': request.POST.get('category', ''),
                'quantity': int(request.POST.get('quantity', 1)),
                'unit': request.POST.get('unit', ''),
                'price': float(request.POST.get('price', 0)) if request.POST.get('price') else None,
                'notes': request.POST.get('notes', '').strip(),
                'brand': request.POST.get('brand', '').strip(),
                'store': request.POST.get('store', '').strip(),
            }

            # Handle optional dates
            expiry_date = request.POST.get('expiry_date')
            if expiry_date:
                update_data['expiry_date'] = expiry_date

            last_purchased = request.POST.get('last_purchased')
            if last_purchased:
                update_data['last_purchased'] = last_purchased

            # Update item
            success = GroceryItemManager.update(item_id, update_data)

            if success:
                messages.success(request, f"Successfully updated {update_data['name']}!")
                logger.info(f"Updated grocery item: {item_id}")
            else:
                messages.error(request, "Failed to update item.")

            return redirect('home')

        except ValueError as e:
            messages.error(request, f"Invalid data: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating grocery item: {e}")
            messages.error(request, "An error occurred while updating the item.")

    # GET request - show form with current data
    from .django_models import GroceryItem
    context = {
        'item': item,
        'categories': [choice[1] for choice in GroceryItem.CATEGORY_CHOICES],
        'units': [choice[1] for choice in GroceryItem.UNIT_CHOICES],
    }

    return render(request, 'grocery_app/edit_item.html', context)


@login_required
def delete_item(request, item_id):
    """
    Delete grocery item
    """
    if request.method == 'POST':
        try:
            # Using GroceryItemManager

            # Get item name for message
            item = GroceryItemManager.get_by_id(item_id)
            item_name = item['name'] if item else 'Item'

            # Delete item
            success = GroceryItemManager.delete(item_id)

            if success:
                messages.success(request, f"Successfully deleted {item_name}!")
                logger.info(f"Deleted grocery item: {item_id}")
            else:
                messages.error(request, "Failed to delete item.")

        except Exception as e:
            logger.error(f"Error deleting grocery item: {e}")
            messages.error(request, "An error occurred while deleting the item.")

    return redirect('home')


@login_required
def dashboard(request):
    """
    Analytics dashboard with AI-powered insights
    """
    try:
        # Using GroceryItemManager
        analytics_model = AnalyticsModel()

        # Get basic statistics
        all_items = GroceryItemManager.get_all()
        total_items = len(all_items)

        # Get expiring items
        expiring_items = GroceryItemManager.get_expiring_items(days=7)

        # Get low stock items
        low_stock_items = GroceryItemManager.get_low_stock_items(threshold=5)

        # Get category statistics
        category_stats = GroceryItemManager.get_categories_stats()

        # Get spending analytics
        spending_analytics = analytics_model.get_spending_analytics(days=30)

        # Calculate total value of inventory using improved function
        from .utils import calculate_total_value, calculate_inventory_statistics

        # Get comprehensive inventory statistics
        inventory_stats = calculate_inventory_statistics(all_items)
        total_value = inventory_stats['active_value']  # Only count active inventory

        # Log inventory statistics for debugging (commented out for production)
        # logger.info(f"Inventory Statistics: {inventory_stats}")

        context = {
            'total_items': total_items,
            'expiring_items': expiring_items,
            'low_stock_items': low_stock_items,
            'category_stats': category_stats,
            'spending_analytics': spending_analytics,
            'total_value': round(total_value, 2),
            'expiring_count': len(expiring_items),
            'low_stock_count': len(low_stock_items),
        }

        return render(request, 'grocery_app/dashboard.html', context)

    except Exception as e:
        logger.error(f"Error in dashboard view: {e}")
        messages.error(request, "An error occurred while loading the dashboard.")
        return render(request, 'grocery_app/dashboard.html', {})


# API Views - Enhanced search functionality is implemented below


# Enhanced suggestions API is implemented below








@csrf_exempt
@require_http_methods(["GET"])
def api_analytics(request):
    """
    API endpoint for analytics data
    """
    try:
        # Using GroceryItemManager
        analytics_model = AnalyticsModel()

        # Get basic stats
        all_items = GroceryItemManager.get_all()
        category_stats = GroceryItemManager.get_categories_stats()
        spending_analytics = analytics_model.get_spending_analytics(days=30)

        # Get expiring items by timeframe
        expiring_today = GroceryItemManager.get_expiring_items(days=0)
        expiring_week = GroceryItemManager.get_expiring_items(days=7)

        return JsonResponse({
            'success': True,
            'total_items': len(all_items),
            'category_stats': category_stats,
            'spending_analytics': spending_analytics,
            'expiring_today': len(expiring_today),
            'expiring_week': len(expiring_week)
        })

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_spending_analytics(request):
    """
    API endpoint for spending analytics with configurable time periods
    """
    try:
        # Get time period from query parameters (default: 30 days)
        days = int(request.GET.get('days', 30))

        # Validate days parameter
        if days < 1 or days > 365:
            return JsonResponse({'success': False, 'error': 'Days must be between 1 and 365'}, status=400)

        # Get all items and calculate spending analytics
        from .utils import calculate_spending_analytics
        all_items = GroceryItemManager.get_all()
        spending_data = calculate_spending_analytics(all_items, days=days)

        return JsonResponse({
            'success': True,
            'spending_analytics': spending_data,
            'period_description': f'Last {days} days'
        })

    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid days parameter'}, status=400)
    except Exception as e:
        logger.error(f"Error getting spending analytics: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_meal_suggestions(request):
    """
    API endpoint for meal suggestions
    """
    try:
        # Using GroceryItemManager
        meal_planner = MealPlanner()

        # Get available items
        available_items = GroceryItemManager.get_all()
        available_items = [item for item in available_items if item.get('quantity', 0) > 0]

        # Get meal suggestions
        suggestions = meal_planner.suggest_meals(available_items)

        return JsonResponse({
            'success': True,
            'meal_suggestions': suggestions
        })

    except Exception as e:
        logger.error(f"Error getting meal suggestions: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_price_comparison(request):
    """
    API endpoint for price comparison
    """
    try:
        item_name = request.GET.get('item', '')

        if not item_name:
            return JsonResponse({'success': False, 'error': 'Item name required'}, status=400)

        from .ai_features import PriceComparison
        price_comparison = PriceComparison()

        prices = price_comparison.compare_prices(item_name)

        return JsonResponse({
            'success': True,
            'item': item_name,
            'prices': prices
        })

    except Exception as e:
        logger.error(f"Error comparing prices: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# AI-Powered Feature Views


def meal_planner(request):
    """
    Meal planner page
    """
    try:
        # Using GroceryItemManager
        meal_planner_engine = MealPlanner()

        # Get available items
        available_items = GroceryItemManager.get_all()
        available_items = [item for item in available_items if item.get('quantity', 0) > 0]

        # Get meal suggestions
        meal_suggestions = meal_planner_engine.suggest_meals(available_items)

        context = {
            'available_items': available_items,
            'meal_suggestions': meal_suggestions,
            'page_title': 'Meal Planner'
        }

        return render(request, 'grocery_app/meal_planner.html', context)

    except Exception as e:
        logger.error(f"Error in meal planner view: {e}")
        messages.error(request, "An error occurred while loading the meal planner.")
        return render(request, 'grocery_app/meal_planner.html', {})


def price_comparison(request):
    """
    Price comparison page
    """
    try:
        # Using GroceryItemManager
        from .ai_features import PriceComparison
        price_engine = PriceComparison()

        # Get all items for comparison
        all_items = GroceryItemManager.get_all()

        # Get best deals
        deals = price_engine.get_best_deals(all_items)

        context = {
            'items': all_items,
            'deals': deals,
            'page_title': 'Price Comparison'
        }

        return render(request, 'grocery_app/price_comparison.html', context)

    except Exception as e:
        logger.error(f"Error in price comparison view: {e}")
        messages.error(request, "An error occurred while loading price comparison.")
        return render(request, 'grocery_app/price_comparison.html', {})


def smart_suggestions(request):
    """
    Smart suggestions page
    """
    try:
        # Using GroceryItemManager
        suggestions_engine = SmartSuggestions()

        # Get user's data
        all_items = GroceryItemManager.get_all()
        current_inventory = [item for item in all_items if item.get('quantity', 0) > 0]

        # Generate different types of suggestions
        purchase_suggestions = suggestions_engine.get_purchase_suggestions(all_items, current_inventory)

        # Get healthier alternatives for current items
        healthier_alternatives = []
        for item in current_inventory[:5]:  # Limit to first 5 items
            alternatives = suggestions_engine.get_healthier_alternatives(item['name'])
            if alternatives:
                healthier_alternatives.append({
                    'original_item': item['name'],
                    'alternatives': alternatives
                })

        context = {
            'purchase_suggestions': purchase_suggestions,
            'healthier_alternatives': healthier_alternatives,
            'current_inventory': current_inventory,
            'page_title': 'Smart Suggestions'
        }

        return render(request, 'grocery_app/smart_suggestions.html', context)

    except Exception as e:
        logger.error(f"Error in smart suggestions view: {e}")
        messages.error(request, "An error occurred while loading smart suggestions.")
        return render(request, 'grocery_app/smart_suggestions.html', {})


def analytics(request):
    """
    Advanced analytics page
    """
    try:
        # Using GroceryItemManager
        analytics_model = AnalyticsModel()

        # Get comprehensive analytics
        all_items = GroceryItemManager.get_all()
        category_stats = GroceryItemManager.get_categories_stats()
        spending_analytics = analytics_model.get_spending_analytics(days=30)

        # Calculate additional metrics using improved function
        from .utils import calculate_total_value, calculate_inventory_statistics
        inventory_stats = calculate_inventory_statistics(all_items)
        total_value = inventory_stats['active_value']

        # Get consumption patterns
        from .django_models import GroceryItem
        consumption_data = []
        for category in [choice[1] for choice in GroceryItem.CATEGORY_CHOICES]:
            category_items = [item for item in all_items if item.get('category') == category]
            if category_items:
                avg_quantity = sum(item.get('quantity', 0) for item in category_items) / len(category_items)
                consumption_data.append({
                    'category': category,
                    'avg_quantity': round(avg_quantity, 2),
                    'item_count': len(category_items)
                })

        context = {
            'total_items': len(all_items),
            'total_value': round(total_value, 2),
            'category_stats': category_stats,
            'spending_analytics': spending_analytics,
            'consumption_data': consumption_data,
            'page_title': 'Analytics'
        }

        return render(request, 'grocery_app/analytics.html', context)

    except Exception as e:
        logger.error(f"Error in analytics view: {e}")
        messages.error(request, "An error occurred while loading analytics.")
        return render(request, 'grocery_app/analytics.html', {})


def reports(request):
    """
    Reports page
    """
    context = {
        'page_title': 'Reports'
    }
    return render(request, 'grocery_app/reports.html', context)


def sustainability(request):
    """
    Sustainability tracking page
    """
    context = {
        'page_title': 'Sustainability Tracker'
    }
    return render(request, 'grocery_app/sustainability.html', context)


def status(request):
    """
    System status page showing all working features
    """
    try:
        # Using GroceryItemManager

        # Get basic stats for status page
        all_items = GroceryItemManager.get_all()
        total_items = len(all_items)

        context = {
            'page_title': 'System Status',
            'total_items': total_items
        }

        return render(request, 'grocery_app/status.html', context)

    except Exception as e:
        logger.error(f"Error in status view: {e}")
        context = {
            'page_title': 'System Status',
            'total_items': 0
        }
        return render(request, 'grocery_app/status.html', context)


# Interactive API Endpoints for Enhanced Functionality

@csrf_exempt
@require_http_methods(["POST", "PUT"])
def api_quick_edit(request, item_id):
    """
    API endpoint for quick editing items (quantity, notes, etc.)
    """
    try:
        # Using GroceryItemManager

        if request.method == 'POST':
            data = json.loads(request.body)
        else:  # PUT
            data = json.loads(request.body)

        # Get current item
        current_item = GroceryItemManager.get_by_id(item_id)
        if not current_item:
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)

        # Update allowed fields
        allowed_fields = ['quantity', 'notes', 'price', 'expiry_date', 'last_purchased']
        update_data = {}

        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if update_data:
            success = GroceryItemManager.update(item_id, update_data)
            if success:
                updated_item = GroceryItemManager.get_by_id(item_id)
                return JsonResponse({
                    'success': True,
                    'message': f'Updated {current_item["name"]} successfully',
                    'item': updated_item
                })
            else:
                return JsonResponse({'success': False, 'error': 'Failed to update item'}, status=500)
        else:
            return JsonResponse({'success': False, 'error': 'No valid fields to update'}, status=400)

    except Exception as e:
        logger.error(f"Error in quick edit: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_quick_delete(request, item_id):
    """
    API endpoint for quick deleting items
    """
    try:
        # Using GroceryItemManager

        # Get item name for response
        item = GroceryItemManager.get_by_id(item_id)
        if not item:
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)

        item_name = item['name']

        # Delete the item
        success = GroceryItemManager.delete(item_id)

        if success:
            return JsonResponse({
                'success': True,
                'message': f'Deleted {item_name} successfully'
            })
        else:
            return JsonResponse({'success': False, 'error': 'Failed to delete item'}, status=500)

    except Exception as e:
        logger.error(f"Error in quick delete: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_bulk_actions(request):
    """
    API endpoint for bulk actions (delete multiple, mark as purchased, etc.)
    """
    try:
        data = json.loads(request.body)
        action = data.get('action')
        item_ids = data.get('item_ids', [])

        if not action or not item_ids:
            return JsonResponse({'success': False, 'error': 'Action and item_ids required'}, status=400)

        # Using GroceryItemManager
        results = []

        if action == 'delete':
            for item_id in item_ids:
                success = GroceryItemManager.delete(item_id)
                results.append({'item_id': item_id, 'success': success})

        elif action == 'mark_purchased':
            for item_id in item_ids:
                success = GroceryItemManager.update(item_id, {
                    'last_purchased': datetime.utcnow(),
                    'quantity': 0  # Mark as consumed
                })
                results.append({'item_id': item_id, 'success': success})

        elif action == 'update_quantity':
            new_quantity = data.get('quantity', 0)
            for item_id in item_ids:
                success = GroceryItemManager.update(item_id, {'quantity': new_quantity})
                results.append({'item_id': item_id, 'success': success})

        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

        successful_count = sum(1 for result in results if result['success'])

        return JsonResponse({
            'success': True,
            'message': f'Successfully processed {successful_count} out of {len(item_ids)} items',
            'results': results
        })

    except Exception as e:
        logger.error(f"Error in bulk actions: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_mark_purchased(request, item_id):
    """
    API endpoint for marking an item as purchased
    """
    try:
        # Using GroceryItemManager

        # Get current item
        item = GroceryItemManager.get_by_id(item_id)
        if not item:
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)

        # Update item as purchased
        update_data = {
            'last_purchased': datetime.utcnow(),
            'quantity': max(0, item.get('quantity', 1) - 1)  # Decrease quantity by 1
        }

        success = GroceryItemManager.update(item_id, update_data)

        if success:
            updated_item = GroceryItemManager.get_by_id(item_id)
            return JsonResponse({
                'success': True,
                'message': f'Marked {item["name"]} as purchased',
                'item': updated_item
            })
        else:
            return JsonResponse({'success': False, 'error': 'Failed to update item'}, status=500)

    except Exception as e:
        logger.error(f"Error marking item as purchased: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_shopping_list(request):
    """
    API endpoint for shopping list management
    """
    try:
        # Using GroceryItemManager

        if request.method == 'GET':
            # Get shopping list (items with quantity > 0)
            all_items = GroceryItemManager.get_all()
            shopping_list = [item for item in all_items if item.get('quantity', 0) > 0]

            # Calculate total estimated cost
            total_cost = sum(item.get('price', 0) * item.get('quantity', 0)
                           for item in shopping_list if item.get('price'))

            return JsonResponse({
                'success': True,
                'shopping_list': shopping_list,
                'total_items': len(shopping_list),
                'estimated_cost': round(total_cost, 2)
            })

        elif request.method == 'POST':
            # Add item to shopping list or update quantity
            data = json.loads(request.body)
            item_name = data.get('name')
            quantity = data.get('quantity', 1)

            if not item_name:
                return JsonResponse({'success': False, 'error': 'Item name required'}, status=400)

            # Check if item already exists
            existing_items = GroceryItemManager.search_items(item_name)
            exact_match = next((item for item in existing_items if item['name'].lower() == item_name.lower()), None)

            if exact_match:
                # Update existing item quantity
                new_quantity = exact_match.get('quantity', 0) + quantity
                success = GroceryItemManager.update(exact_match['id'], {'quantity': new_quantity})
                message = f'Updated {item_name} quantity to {new_quantity}'
            else:
                # Create new item
                item_data = {
                    'name': item_name,
                    'category': data.get('category', 'Other'),
                    'quantity': quantity,
                    'unit': data.get('unit', 'pieces'),
                    'price': data.get('price'),
                    'notes': f'Added to shopping list on {datetime.utcnow().strftime("%Y-%m-%d")}'
                }
                item_id = GroceryItemManager.create(item_data)
                success = bool(item_id)
                message = f'Added {item_name} to shopping list'

            return JsonResponse({
                'success': success,
                'message': message
            })

    except Exception as e:
        logger.error(f"Error in shopping list API: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_notifications(request):
    """
    API endpoint for getting notifications (expiring items, low stock, etc.)
    """
    try:
        # Using GroceryItemManager

        notifications = []

        # Check for expiring items
        expiring_today = GroceryItemManager.get_expiring_items(days=0)
        expiring_soon = GroceryItemManager.get_expiring_items(days=3)

        for item in expiring_today:
            notifications.append({
                'type': 'urgent',
                'title': 'Item Expiring Today!',
                'message': f'{item["name"]} expires today',
                'item_id': item['id'],
                'action': 'use_now'
            })

        for item in expiring_soon:
            if item not in expiring_today:
                notifications.append({
                    'type': 'warning',
                    'title': 'Item Expiring Soon',
                    'message': f'{item["name"]} expires in {calculate_days_until_expiry(item.get("expiry_date"))} days',
                    'item_id': item['id'],
                    'action': 'plan_usage'
                })

        # Check for low stock items
        low_stock_items = GroceryItemManager.get_low_stock_items(threshold=2)
        for item in low_stock_items:
            notifications.append({
                'type': 'info',
                'title': 'Low Stock Alert',
                'message': f'Only {item["quantity"]} {item["unit"]} of {item["name"]} remaining',
                'item_id': item['id'],
                'action': 'restock'
            })

        # Check for items not purchased in a while
        all_items = GroceryItemManager.get_all()
        stale_items = []
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        for item in all_items:
            last_purchased = item.get('last_purchased')
            if last_purchased and last_purchased < thirty_days_ago:
                stale_items.append(item)

        if stale_items:
            notifications.append({
                'type': 'suggestion',
                'title': 'Restock Suggestion',
                'message': f'{len(stale_items)} items haven\'t been purchased in 30+ days',
                'action': 'review_list'
            })

        return JsonResponse({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        })

    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Helper functions for enhanced functionality

def calculate_days_until_expiry(expiry_date):
    """Calculate days until expiry date"""
    if not expiry_date:
        return None

    if isinstance(expiry_date, str):
        try:
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')
        except ValueError:
            return None

    today = datetime.utcnow().date()
    if hasattr(expiry_date, 'date'):
        expiry_date = expiry_date.date()

    delta = expiry_date - today
    return delta.days


def get_csrf_token_for_js():
    """Helper function to get CSRF token for JavaScript"""
    from django.middleware.csrf import get_token
    from django.http import HttpRequest

    request = HttpRequest()
    return get_token(request)


# Enhanced API endpoints for better functionality

@csrf_exempt
@require_http_methods(["GET"])
def api_search_items(request):
    """
    Enhanced search API with better filtering and suggestions
    """
    try:
        query = request.GET.get('q', '').strip()
        category = request.GET.get('category', '')
        limit = int(request.GET.get('limit', 10))

        # Using GroceryItemManager

        if not query and not category:
            # Return all items if no search criteria
            items = GroceryItemManager.get_all()
        elif not query:
            # Filter by category only
            items = GroceryItemManager.get_all()
            items = [item for item in items if item.get('category', '').lower() == category.lower()]
        else:
            # Search items
            items = GroceryItemManager.search_items(query)

            # Filter by category if specified
            if category:
                items = [item for item in items if item.get('category', '').lower() == category.lower()]

        # Limit results
        items = items[:limit]

        # Add relevance scoring only if there's a query
        if query:
            for item in items:
                item['relevance'] = calculate_relevance(item['name'], query)
            # Sort by relevance
            items.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        else:
            # Sort by name if no query
            items.sort(key=lambda x: x.get('name', '').lower())

        return JsonResponse({
            'success': True,
            'items': items,
            'count': len(items),
            'query': query
        })

    except Exception as e:
        logger.error(f"Error in search API: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def calculate_relevance(item_name, query):
    """Calculate relevance score for search results"""
    item_name_lower = item_name.lower()
    query_lower = query.lower()

    # Exact match gets highest score
    if item_name_lower == query_lower:
        return 100

    # Starts with query gets high score
    if item_name_lower.startswith(query_lower):
        return 80

    # Contains query gets medium score
    if query_lower in item_name_lower:
        return 60

    # Word match gets lower score
    query_words = query_lower.split()
    item_words = item_name_lower.split()

    matches = sum(1 for word in query_words if any(word in item_word for item_word in item_words))
    if matches > 0:
        return 40 + (matches * 10)

    return 0


@csrf_exempt
@require_http_methods(["GET"])
def api_get_suggestions(request):
    """
    Enhanced suggestions API with AI-powered recommendations
    """
    try:
        # Using GroceryItemManager

        # Get all items for analysis
        all_items = GroceryItemManager.get_all()

        suggestions = []

        # Suggest items that are running low
        low_stock_items = GroceryItemManager.get_low_stock_items(threshold=3)
        for item in low_stock_items:
            suggestions.append({
                'name': item['name'],
                'category': item['category'],
                'suggested_quantity': max(5, item.get('quantity', 1) * 2),
                'unit': item['unit'],
                'reason': f'Running low (only {item.get("quantity", 0)} left)',
                'priority': 'high'
            })

        # Suggest items that haven't been purchased recently
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        for item in all_items:
            last_purchased = item.get('last_purchased')
            if last_purchased and last_purchased < thirty_days_ago:
                suggestions.append({
                    'name': item['name'],
                    'category': item['category'],
                    'suggested_quantity': item.get('quantity', 1),
                    'unit': item['unit'],
                    'reason': 'Haven\'t purchased in 30+ days',
                    'priority': 'medium'
                })

        # Suggest seasonal items
        seasonal_suggestions = get_seasonal_suggestions()
        suggestions.extend(seasonal_suggestions)

        # Sort by priority and limit results
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        suggestions.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 1), reverse=True)

        return JsonResponse({
            'success': True,
            'suggestions': suggestions[:10]  # Limit to top 10
        })

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def get_seasonal_suggestions():
    """Get seasonal item suggestions based on current month"""
    import calendar

    current_month = datetime.utcnow().month
    seasonal_items = {
        1: [  # January
            {'name': 'Oranges', 'category': 'Fruits & Vegetables', 'reason': 'Citrus season'},
            {'name': 'Soup', 'category': 'Pantry Staples', 'reason': 'Winter comfort food'}
        ],
        2: [  # February
            {'name': 'Chocolate', 'category': 'Snacks', 'reason': 'Valentine\'s Day'},
            {'name': 'Strawberries', 'category': 'Fruits & Vegetables', 'reason': 'Valentine\'s Day'}
        ],
        3: [  # March
            {'name': 'Asparagus', 'category': 'Fruits & Vegetables', 'reason': 'Spring vegetables'},
            {'name': 'Spinach', 'category': 'Fruits & Vegetables', 'reason': 'Spring greens'}
        ],
        4: [  # April
            {'name': 'Artichokes', 'category': 'Fruits & Vegetables', 'reason': 'Spring season'},
            {'name': 'Peas', 'category': 'Fruits & Vegetables', 'reason': 'Spring vegetables'}
        ],
        5: [  # May
            {'name': 'Strawberries', 'category': 'Fruits & Vegetables', 'reason': 'Berry season'},
            {'name': 'Lettuce', 'category': 'Fruits & Vegetables', 'reason': 'Spring salads'}
        ],
        6: [  # June
            {'name': 'Berries', 'category': 'Fruits & Vegetables', 'reason': 'Summer berry season'},
            {'name': 'Zucchini', 'category': 'Fruits & Vegetables', 'reason': 'Summer squash'}
        ],
        7: [  # July
            {'name': 'Tomatoes', 'category': 'Fruits & Vegetables', 'reason': 'Peak tomato season'},
            {'name': 'Corn', 'category': 'Fruits & Vegetables', 'reason': 'Summer corn'}
        ],
        8: [  # August
            {'name': 'Peaches', 'category': 'Fruits & Vegetables', 'reason': 'Stone fruit season'},
            {'name': 'Watermelon', 'category': 'Fruits & Vegetables', 'reason': 'Summer hydration'}
        ],
        9: [  # September
            {'name': 'Apples', 'category': 'Fruits & Vegetables', 'reason': 'Apple harvest'},
            {'name': 'Pumpkin', 'category': 'Fruits & Vegetables', 'reason': 'Fall season'}
        ],
        10: [  # October
            {'name': 'Squash', 'category': 'Fruits & Vegetables', 'reason': 'Fall harvest'},
            {'name': 'Sweet Potatoes', 'category': 'Fruits & Vegetables', 'reason': 'Fall vegetables'}
        ],
        11: [  # November
            {'name': 'Turkey', 'category': 'Meat & Seafood', 'reason': 'Thanksgiving'},
            {'name': 'Cranberries', 'category': 'Fruits & Vegetables', 'reason': 'Thanksgiving'}
        ],
        12: [  # December
            {'name': 'Ham', 'category': 'Meat & Seafood', 'reason': 'Holiday season'},
            {'name': 'Eggnog', 'category': 'Dairy & Eggs', 'reason': 'Holiday drinks'}
        ]
    }

    suggestions = []
    month_items = seasonal_items.get(current_month, [])

    for item in month_items:
        suggestions.append({
            'name': item['name'],
            'category': item['category'],
            'suggested_quantity': 1,
            'unit': 'pieces',
            'reason': item['reason'],
            'priority': 'low'
        })

    return suggestions
