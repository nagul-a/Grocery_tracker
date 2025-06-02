"""
Django ORM Models for Smart Grocery Tracker

This module defines Django models using SQLite database for easy setup.
"""

from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger('grocery_app')


class GroceryItem(models.Model):
    """
    Django model for grocery items
    """
    
    # Predefined categories
    CATEGORY_CHOICES = [
        ('Fruits & Vegetables', 'Fruits & Vegetables'),
        ('Dairy & Eggs', 'Dairy & Eggs'),
        ('Meat & Seafood', 'Meat & Seafood'),
        ('Bakery', 'Bakery'),
        ('Pantry Staples', 'Pantry Staples'),
        ('Frozen Foods', 'Frozen Foods'),
        ('Beverages', 'Beverages'),
        ('Snacks', 'Snacks'),
        ('Health & Beauty', 'Health & Beauty'),
        ('Household Items', 'Household Items'),
        ('Other', 'Other'),
    ]
    
    UNIT_CHOICES = [
        ('pieces', 'Pieces'),
        ('kg', 'Kilograms'),
        ('grams', 'Grams'),
        ('liters', 'Liters'),
        ('ml', 'Milliliters'),
        ('packets', 'Packets'),
        ('bottles', 'Bottles'),
        ('cans', 'Cans'),
        ('boxes', 'Boxes'),
        ('loaf', 'Loaf'),
        ('cups', 'Cups'),
        ('block', 'Block'),
    ]
    
    # Basic fields
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    quantity = models.IntegerField(default=1)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pieces')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Date fields
    expiry_date = models.DateTimeField(null=True, blank=True)
    last_purchased = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional fields
    notes = models.TextField(blank=True)
    barcode = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    store = models.CharField(max_length=100, blank=True)
    
    # Nutritional info as JSON field
    nutritional_info = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"
    
    @property
    def days_until_expiry(self):
        """Calculate days until expiry"""
        if self.expiry_date:
            delta = self.expiry_date.date() - timezone.now().date()
            return delta.days
        return None
    
    @property
    def is_expiring_soon(self):
        """Check if item is expiring within 7 days"""
        days = self.days_until_expiry
        return days is not None and days <= 7
    
    @property
    def is_low_stock(self):
        """Check if item is low stock (quantity <= 3)"""
        return self.quantity <= 3
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'category': self.category,
            'quantity': self.quantity,
            'unit': self.unit,
            'price': float(self.price) if self.price else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'last_purchased': self.last_purchased.isoformat() if self.last_purchased else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes,
            'barcode': self.barcode,
            'brand': self.brand,
            'store': self.store,
            'nutritional_info': self.nutritional_info,
            'days_until_expiry': self.days_until_expiry,
            'is_expiring_soon': self.is_expiring_soon,
            'is_low_stock': self.is_low_stock,
        }


class GroceryItemManager:
    """
    Manager class to provide MongoDB-like interface for Django ORM
    """
    
    @staticmethod
    def get_all(filters=None):
        """Get all grocery items with optional filters - optimized"""
        queryset = GroceryItem.objects.select_related().all()

        if filters:
            if 'category' in filters:
                queryset = queryset.filter(category=filters['category'])
            if 'name' in filters:
                queryset = queryset.filter(name__icontains=filters['name'])

        # Use only() to fetch only required fields for better performance
        queryset = queryset.only('id', 'name', 'category', 'quantity', 'unit', 'price', 'expiry_date', 'last_purchased', 'notes')

        return [item.to_dict() for item in queryset]
    
    @staticmethod
    def get_by_id(item_id):
        """Get grocery item by ID"""
        try:
            item = GroceryItem.objects.get(id=item_id)
            return item.to_dict()
        except GroceryItem.DoesNotExist:
            return None
    
    @staticmethod
    def create(item_data):
        """Create a new grocery item"""
        try:
            # Handle datetime fields
            if 'expiry_date' in item_data and isinstance(item_data['expiry_date'], str):
                item_data['expiry_date'] = datetime.fromisoformat(item_data['expiry_date'])
            if 'last_purchased' in item_data and isinstance(item_data['last_purchased'], str):
                item_data['last_purchased'] = datetime.fromisoformat(item_data['last_purchased'])
            
            item = GroceryItem.objects.create(**item_data)
            logger.info(f"Created grocery item: {item.name}")
            return str(item.id)
        except Exception as e:
            logger.error(f"Error creating grocery item: {e}")
            raise
    
    @staticmethod
    def update(item_id, update_data):
        """Update grocery item"""
        try:
            item = GroceryItem.objects.get(id=item_id)
            
            # Handle datetime fields
            if 'expiry_date' in update_data and isinstance(update_data['expiry_date'], str):
                update_data['expiry_date'] = datetime.fromisoformat(update_data['expiry_date'])
            if 'last_purchased' in update_data and isinstance(update_data['last_purchased'], str):
                update_data['last_purchased'] = datetime.fromisoformat(update_data['last_purchased'])
            
            for key, value in update_data.items():
                setattr(item, key, value)
            
            item.save()
            logger.info(f"Updated grocery item: {item.name}")
            return True
        except GroceryItem.DoesNotExist:
            logger.error(f"Item with ID {item_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error updating grocery item: {e}")
            return False
    
    @staticmethod
    def delete(item_id):
        """Delete grocery item"""
        try:
            item = GroceryItem.objects.get(id=item_id)
            item_name = item.name
            item.delete()
            logger.info(f"Deleted grocery item: {item_name}")
            return True
        except GroceryItem.DoesNotExist:
            logger.error(f"Item with ID {item_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error deleting grocery item: {e}")
            return False
    
    @staticmethod
    def search_items(query):
        """Search grocery items by name - optimized"""
        items = GroceryItem.objects.filter(name__icontains=query).only(
            'id', 'name', 'category', 'quantity', 'unit', 'price', 'expiry_date', 'notes'
        )[:20]  # Limit results for performance
        return [item.to_dict() for item in items]
    
    @staticmethod
    def get_expiring_items(days=7):
        """Get items expiring within specified days"""
        cutoff_date = timezone.now() + timedelta(days=days)
        items = GroceryItem.objects.filter(
            expiry_date__lte=cutoff_date,
            expiry_date__gte=timezone.now()
        )
        return [item.to_dict() for item in items]
    
    @staticmethod
    def get_low_stock_items(threshold=3):
        """Get items with low stock"""
        items = GroceryItem.objects.filter(quantity__lte=threshold)
        return [item.to_dict() for item in items]
    
    @staticmethod
    def get_categories_stats():
        """Get statistics by category"""
        from django.db.models import Count, Sum
        
        stats = GroceryItem.objects.values('category').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity')
        )
        
        return list(stats)


class AnalyticsModel:
    """Analytics model for grocery data"""
    
    @staticmethod
    def get_spending_analytics(days=30):
        """Get comprehensive spending analytics for the last N days"""
        from .utils import calculate_spending_analytics

        # Get all items and use the enhanced calculation function
        all_items = GroceryItemManager.get_all()

        # Use the enhanced spending analytics function
        spending_data = calculate_spending_analytics(all_items, days=days)

        # Maintain backward compatibility with existing template structure
        return {
            'total_spent': spending_data['total_spent'],
            'period_days': spending_data['period_days'],
            'avg_daily_spending': spending_data['avg_daily_spending'],
            'average_per_day': spending_data['avg_daily_spending'],  # Backward compatibility
            'category_breakdown': spending_data['category_breakdown'],
            'items_purchased': spending_data['items_purchased'],
            'avg_item_cost': spending_data['avg_item_cost'],
            'recent_purchases': spending_data['recent_purchases']
        }
