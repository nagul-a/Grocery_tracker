"""
Utility functions for Smart Grocery Tracker

This module contains helper functions for date formatting,
calculations, and other common operations.
"""

from datetime import datetime, date, timedelta
from typing import Optional, Union, Dict, Any
import logging

logger = logging.getLogger('grocery_app')


def format_date(date_obj: Union[datetime, date, str, None], format_str: str = "%Y-%m-%d") -> str:
    """
    Format date object to string

    Args:
        date_obj: Date object, datetime object, or date string
        format_str: Format string for output

    Returns:
        Formatted date string or empty string if invalid
    """
    try:
        if date_obj is None:
            return ""

        if isinstance(date_obj, str):
            # Try to parse string date
            try:
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
                except ValueError:
                    return date_obj  # Return original string if can't parse

        if isinstance(date_obj, datetime):
            return date_obj.strftime(format_str)
        elif isinstance(date_obj, date):
            return date_obj.strftime(format_str)

        return str(date_obj)

    except Exception as e:
        logger.error(f"Error formatting date {date_obj}: {e}")
        return ""


def calculate_days_until_expiry(expiry_date: Union[datetime, date, str, None]) -> Optional[int]:
    """
    Calculate days until expiry

    Args:
        expiry_date: Expiry date as datetime, date, or string

    Returns:
        Number of days until expiry (negative if expired) or None if invalid
    """
    try:
        if expiry_date is None:
            return None

        if isinstance(expiry_date, str):
            try:
                expiry_date = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
            except ValueError:
                try:
                    expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
                except ValueError:
                    return None

        if isinstance(expiry_date, datetime):
            expiry_date = expiry_date.date()

        if isinstance(expiry_date, date):
            today = date.today()
            delta = expiry_date - today
            return delta.days

        return None

    except Exception as e:
        logger.error(f"Error calculating days until expiry for {expiry_date}: {e}")
        return None


def get_expiry_status(expiry_date: Union[datetime, date, str, None]) -> Dict[str, Any]:
    """
    Get expiry status with color coding and message

    Args:
        expiry_date: Expiry date

    Returns:
        Dictionary with status, color, and message
    """
    try:
        days_until_expiry = calculate_days_until_expiry(expiry_date)

        if days_until_expiry is None:
            return {
                'status': 'unknown',
                'color': 'secondary',
                'message': 'No expiry date',
                'days': None
            }

        if days_until_expiry < 0:
            return {
                'status': 'expired',
                'color': 'danger',
                'message': f'Expired {abs(days_until_expiry)} days ago',
                'days': days_until_expiry
            }
        elif days_until_expiry == 0:
            return {
                'status': 'expires_today',
                'color': 'danger',
                'message': 'Expires today',
                'days': days_until_expiry
            }
        elif days_until_expiry <= 3:
            return {
                'status': 'expires_soon',
                'color': 'warning',
                'message': f'Expires in {days_until_expiry} days',
                'days': days_until_expiry
            }
        elif days_until_expiry <= 7:
            return {
                'status': 'expires_this_week',
                'color': 'info',
                'message': f'Expires in {days_until_expiry} days',
                'days': days_until_expiry
            }
        else:
            return {
                'status': 'fresh',
                'color': 'success',
                'message': f'Expires in {days_until_expiry} days',
                'days': days_until_expiry
            }

    except Exception as e:
        logger.error(f"Error getting expiry status: {e}")
        return {
            'status': 'error',
            'color': 'secondary',
            'message': 'Error checking expiry',
            'days': None
        }


def calculate_stock_level(quantity: int, threshold_low: int = 5, threshold_medium: int = 10) -> Dict[str, Any]:
    """
    Calculate stock level status

    Args:
        quantity: Current quantity
        threshold_low: Low stock threshold
        threshold_medium: Medium stock threshold

    Returns:
        Dictionary with stock level info
    """
    try:
        if quantity <= 0:
            return {
                'level': 'out_of_stock',
                'color': 'danger',
                'message': 'Out of stock',
                'icon': 'exclamation-triangle'
            }
        elif quantity <= threshold_low:
            return {
                'level': 'low',
                'color': 'warning',
                'message': 'Low stock',
                'icon': 'exclamation-circle'
            }
        elif quantity <= threshold_medium:
            return {
                'level': 'medium',
                'color': 'info',
                'message': 'Medium stock',
                'icon': 'info-circle'
            }
        else:
            return {
                'level': 'high',
                'color': 'success',
                'message': 'Good stock',
                'icon': 'check-circle'
            }

    except Exception as e:
        logger.error(f"Error calculating stock level: {e}")
        return {
            'level': 'unknown',
            'color': 'secondary',
            'message': 'Unknown',
            'icon': 'question-circle'
        }


def format_currency(amount: Optional[float], currency_symbol: str = "₹") -> str:
    """
    Format currency amount

    Args:
        amount: Amount to format
        currency_symbol: Currency symbol

    Returns:
        Formatted currency string
    """
    try:
        if amount is None:
            return "N/A"

        return f"{currency_symbol}{amount:.2f}"

    except Exception as e:
        logger.error(f"Error formatting currency {amount}: {e}")
        return "N/A"


def calculate_total_value(items: list, include_zero_quantity: bool = False) -> float:
    """
    Calculate total value of grocery items with improved error handling

    Args:
        items: List of grocery items with price and quantity
        include_zero_quantity: Whether to include items with zero quantity (default: False)

    Returns:
        Total value as float, rounded to 2 decimal places
    """
    try:
        total = 0.0

        for item in items:
            # Get price and quantity with proper null handling
            price = item.get('price')
            quantity = item.get('quantity')

            # Skip items without price or quantity data
            if price is None or quantity is None:
                continue

            # Convert to float if needed (handles Decimal fields)
            try:
                price_float = float(price) if price is not None else 0.0
                quantity_int = int(quantity) if quantity is not None else 0
            except (ValueError, TypeError):
                logger.warning(f"Invalid price/quantity data for item {item.get('name', 'Unknown')}: price={price}, quantity={quantity}")
                continue

            # Skip items with zero or negative values unless explicitly included
            if not include_zero_quantity and quantity_int <= 0:
                continue

            if price_float <= 0:
                continue

            # Calculate item total value
            item_total = price_float * quantity_int
            total += item_total

            # Log for debugging (can be removed in production)
            # logger.debug(f"Item: {item.get('name', 'Unknown')}, Price: ₹{price_float}, Quantity: {quantity_int}, Total: ₹{item_total}")

        return round(total, 2)

    except Exception as e:
        logger.error(f"Error calculating total value: {e}")
        return 0.0


def calculate_inventory_statistics(items: list) -> dict:
    """
    Calculate comprehensive inventory statistics

    Args:
        items: List of grocery items

    Returns:
        Dictionary with inventory statistics
    """
    try:
        stats = {
            'total_items': 0,
            'active_items': 0,
            'total_value': 0.0,
            'active_value': 0.0,
            'items_with_price': 0,
            'items_without_price': 0,
            'zero_quantity_items': 0,
            'categories': set(),
            'average_item_value': 0.0
        }

        total_value_all = 0.0
        total_value_active = 0.0
        active_items_count = 0
        items_with_value = 0

        for item in items:
            stats['total_items'] += 1

            # Get item data
            price = item.get('price')
            quantity = item.get('quantity', 0)
            category = item.get('category')

            # Track categories
            if category:
                stats['categories'].add(category)

            # Count items by price availability
            if price is not None and price > 0:
                stats['items_with_price'] += 1

                try:
                    price_float = float(price)
                    quantity_int = int(quantity) if quantity is not None else 0

                    item_value = price_float * quantity_int
                    total_value_all += item_value

                    if quantity_int > 0:
                        stats['active_items'] += 1
                        total_value_active += item_value
                        active_items_count += 1
                        items_with_value += 1
                    else:
                        stats['zero_quantity_items'] += 1

                except (ValueError, TypeError):
                    logger.warning(f"Invalid data for item {item.get('name', 'Unknown')}")
                    stats['items_without_price'] += 1
            else:
                stats['items_without_price'] += 1
                if quantity is not None and quantity <= 0:
                    stats['zero_quantity_items'] += 1

        # Calculate final statistics
        stats['total_value'] = round(total_value_all, 2)
        stats['active_value'] = round(total_value_active, 2)
        stats['categories'] = len(stats['categories'])

        # Calculate average item value (for active items with price)
        if items_with_value > 0:
            stats['average_item_value'] = round(total_value_active / items_with_value, 2)

        return stats

    except Exception as e:
        logger.error(f"Error calculating inventory statistics: {e}")
        return {
            'total_items': 0,
            'active_items': 0,
            'total_value': 0.0,
            'active_value': 0.0,
            'items_with_price': 0,
            'items_without_price': 0,
            'zero_quantity_items': 0,
            'categories': 0,
            'average_item_value': 0.0
        }


def calculate_spending_analytics(items: list, days: int = 30) -> dict:
    """
    Calculate comprehensive spending analytics for grocery items

    Args:
        items: List of grocery items with purchase data
        days: Number of days to look back for spending calculation (default: 30)

    Returns:
        Dictionary with spending analytics including:
        - total_spent: Total amount spent in the period
        - category_breakdown: Spending breakdown by category
        - period_days: Number of days in the analysis period
        - avg_daily_spending: Average spending per day
        - items_purchased: Number of items purchased in period
        - avg_item_cost: Average cost per item purchased
    """
    try:
        from datetime import datetime, timedelta
        from django.utils import timezone

        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)

        analytics = {
            'total_spent': 0.0,
            'category_breakdown': {},
            'period_days': days,
            'avg_daily_spending': 0.0,
            'items_purchased': 0,
            'avg_item_cost': 0.0,
            'spending_by_week': [],
            'recent_purchases': []
        }

        total_spent = 0.0
        items_purchased = 0
        category_totals = {}
        recent_purchases = []

        for item in items:
            # Get item data
            price = item.get('price')
            quantity = item.get('quantity', 0)
            last_purchased = item.get('last_purchased')
            category = item.get('category', 'Other')
            name = item.get('name', 'Unknown')

            # Skip items without price or purchase date
            if not price or not last_purchased:
                continue

            # Parse last_purchased date if it's a string
            if isinstance(last_purchased, str):
                try:
                    from dateutil import parser
                    last_purchased = parser.parse(last_purchased)
                    if last_purchased.tzinfo is None:
                        last_purchased = timezone.make_aware(last_purchased)
                except:
                    continue

            # Check if purchase is within the specified period
            if last_purchased < cutoff_date:
                continue

            try:
                price_float = float(price) if price is not None else 0.0
                quantity_int = int(quantity) if quantity is not None else 1

                # For spending analytics, we assume the full quantity was purchased
                # on the last_purchased date (this is a simplification)
                item_total_cost = price_float * quantity_int

                total_spent += item_total_cost
                items_purchased += 1

                # Track by category
                if category not in category_totals:
                    category_totals[category] = {
                        'total_spent': 0.0,
                        'item_count': 0,
                        'avg_price': 0.0,
                        'category_name': category
                    }

                category_totals[category]['total_spent'] += item_total_cost
                category_totals[category]['item_count'] += 1

                # Track recent purchases for detailed view
                recent_purchases.append({
                    'name': name,
                    'category': category,
                    'price': price_float,
                    'quantity': quantity_int,
                    'total_cost': item_total_cost,
                    'purchase_date': last_purchased,
                    'days_ago': (timezone.now() - last_purchased).days
                })

            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid price/quantity data for item {name}: {e}")
                continue

        # Calculate category averages
        for category_data in category_totals.values():
            if category_data['item_count'] > 0:
                category_data['avg_price'] = round(
                    category_data['total_spent'] / category_data['item_count'], 2
                )

        # Sort categories by spending (highest first)
        category_breakdown = sorted(
            category_totals.values(),
            key=lambda x: x['total_spent'],
            reverse=True
        )

        # Sort recent purchases by date (most recent first)
        recent_purchases.sort(key=lambda x: x['purchase_date'], reverse=True)

        # Calculate final analytics
        analytics.update({
            'total_spent': round(total_spent, 2),
            'category_breakdown': category_breakdown,
            'avg_daily_spending': round(total_spent / days, 2) if days > 0 else 0.0,
            'items_purchased': items_purchased,
            'avg_item_cost': round(total_spent / items_purchased, 2) if items_purchased > 0 else 0.0,
            'recent_purchases': recent_purchases[:10]  # Limit to 10 most recent
        })

        return analytics

    except Exception as e:
        logger.error(f"Error calculating spending analytics: {e}")
        return {
            'total_spent': 0.0,
            'category_breakdown': [],
            'period_days': days,
            'avg_daily_spending': 0.0,
            'items_purchased': 0,
            'avg_item_cost': 0.0,
            'spending_by_week': [],
            'recent_purchases': []
        }


def get_category_icon(category: str) -> str:
    """
    Get icon for grocery category

    Args:
        category: Category name

    Returns:
        Bootstrap icon class name
    """
    category_icons = {
        'Fruits & Vegetables': 'apple',
        'Dairy & Eggs': 'egg',
        'Meat & Seafood': 'fish',
        'Bakery': 'bread-slice',
        'Pantry Staples': 'jar',
        'Frozen Foods': 'snow',
        'Beverages': 'cup-straw',
        'Snacks': 'cookie',
        'Health & Beauty': 'heart',
        'Household Items': 'house',
        'Other': 'bag'
    }

    return category_icons.get(category, 'bag')


def validate_grocery_item(item_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate grocery item data

    Args:
        item_data: Dictionary containing item data

    Returns:
        Dictionary with validation results
    """
    try:
        errors = []
        warnings = []

        # Required fields
        required_fields = ['name', 'category', 'quantity', 'unit']
        for field in required_fields:
            if field not in item_data or not item_data[field]:
                errors.append(f"{field.title()} is required")

        # Validate quantity
        try:
            quantity = int(item_data.get('quantity', 0))
            if quantity <= 0:
                errors.append("Quantity must be greater than 0")
        except (ValueError, TypeError):
            errors.append("Quantity must be a valid number")

        # Validate price
        if 'price' in item_data and item_data['price']:
            try:
                price = float(item_data['price'])
                if price < 0:
                    errors.append("Price cannot be negative")
            except (ValueError, TypeError):
                errors.append("Price must be a valid number")

        # Validate dates
        if 'expiry_date' in item_data and item_data['expiry_date']:
            try:
                expiry_date = datetime.fromisoformat(str(item_data['expiry_date']))
                if expiry_date.date() < date.today():
                    warnings.append("Expiry date is in the past")
            except (ValueError, TypeError):
                errors.append("Invalid expiry date format")

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    except Exception as e:
        logger.error(f"Error validating grocery item: {e}")
        return {
            'is_valid': False,
            'errors': ['Validation error occurred'],
            'warnings': []
        }


def search_items_fuzzy(items: list, search_term: str, fields: list = None) -> list:
    """
    Perform fuzzy search on grocery items

    Args:
        items: List of grocery items
        search_term: Search term
        fields: Fields to search in (default: name, category, brand)

    Returns:
        Filtered list of items
    """
    try:
        if not search_term:
            return items

        if fields is None:
            fields = ['name', 'category', 'brand', 'notes']

        search_term = search_term.lower()
        filtered_items = []

        for item in items:
            for field in fields:
                field_value = str(item.get(field, '')).lower()
                if search_term in field_value:
                    filtered_items.append(item)
                    break

        return filtered_items

    except Exception as e:
        logger.error(f"Error in fuzzy search: {e}")
        return items
