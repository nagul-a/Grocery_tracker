"""
Django Models for Smart Grocery Tracker

This module defines Django ORM models for the grocery tracking application.
Uses SQLite database for easy setup and deployment.
"""

from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
import json
from pymongo import MongoClient
from bson import ObjectId

logger = logging.getLogger('grocery_app')

# Import the Django models
from .django_models import GroceryItem, GroceryItemManager, AnalyticsModel


class MongoDBConnection:
    """Singleton MongoDB connection manager"""
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self.connect()

    def connect(self):
        """Establish MongoDB connection"""
        try:
            mongo_settings = settings.MONGODB_SETTINGS

            # Build connection string
            if mongo_settings['username'] and mongo_settings['password']:
                connection_string = f"mongodb://{mongo_settings['username']}:{mongo_settings['password']}@{mongo_settings['host']}:{mongo_settings['port']}/{mongo_settings['db_name']}"
            else:
                connection_string = f"mongodb://{mongo_settings['host']}:{mongo_settings['port']}"

            self._client = MongoClient(connection_string)
            self._db = self._client[mongo_settings['db_name']]

            # Test connection
            self._client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            # Fallback to local MongoDB without auth
            try:
                self._client = MongoClient('mongodb://localhost:27017/')
                self._db = self._client['smart_grocery_tracker']
                self._client.admin.command('ping')
                logger.info("Connected to local MongoDB without authentication")
            except Exception as fallback_error:
                logger.error(f"Fallback connection also failed: {fallback_error}")
                raise

    def get_database(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db

    def get_collection(self, collection_name: str):
        """Get collection instance"""
        return self.get_database()[collection_name]


class GroceryItem:
    """
    Grocery Item Model for MongoDB

    Schema:
    {
        "_id": ObjectId,
        "name": str,
        "category": str,
        "quantity": int,
        "unit": str,
        "expiry_date": datetime (optional),
        "last_purchased": datetime (optional),
        "price": float (optional),
        "user_id": str (optional),
        "created_at": datetime,
        "updated_at": datetime,
        "notes": str (optional),
        "nutritional_info": dict (optional),
        "barcode": str (optional),
        "brand": str (optional),
        "store": str (optional)
    }
    """

    COLLECTION_NAME = 'grocery_items'

    # Predefined categories
    CATEGORIES = [
        'Fruits & Vegetables',
        'Dairy & Eggs',
        'Meat & Seafood',
        'Bakery',
        'Pantry Staples',
        'Frozen Foods',
        'Beverages',
        'Snacks',
        'Health & Beauty',
        'Household Items',
        'Other'
    ]

    # Common units
    UNITS = [
        'pieces', 'kg', 'g', 'lbs', 'oz',
        'liters', 'ml', 'gallons', 'cups',
        'packages', 'boxes', 'cans', 'bottles'
    ]

    def __init__(self):
        self.db_connection = MongoDBConnection()
        self.collection = self.db_connection.get_collection(self.COLLECTION_NAME)

    def create(self, item_data: Dict[str, Any]) -> str:
        """Create a new grocery item"""
        try:
            # Add timestamps
            now = datetime.utcnow()
            item_data['created_at'] = now
            item_data['updated_at'] = now

            # Validate required fields
            required_fields = ['name', 'category', 'quantity', 'unit']
            for field in required_fields:
                if field not in item_data or not item_data[field]:
                    raise ValueError(f"Required field '{field}' is missing or empty")

            # Convert date strings to datetime objects if needed
            if 'expiry_date' in item_data and isinstance(item_data['expiry_date'], str):
                item_data['expiry_date'] = datetime.fromisoformat(item_data['expiry_date'])

            if 'last_purchased' in item_data and isinstance(item_data['last_purchased'], str):
                item_data['last_purchased'] = datetime.fromisoformat(item_data['last_purchased'])

            # Insert item
            result = self.collection.insert_one(item_data)
            logger.info(f"Created grocery item: {item_data['name']}")
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Error creating grocery item: {e}")
            raise

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get grocery item by ID"""
        try:
            item = self.collection.find_one({"_id": ObjectId(item_id)})
            if item:
                item['id'] = str(item['_id'])
                del item['_id']
            return item
        except Exception as e:
            logger.error(f"Error getting grocery item by ID {item_id}: {e}")
            return None

    def get_all(self, user_id: Optional[str] = None, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Get all grocery items with optional filtering"""
        try:
            query = {}

            # Add user filter if provided
            if user_id:
                query['user_id'] = user_id

            # Add additional filters
            if filters:
                if 'category' in filters and filters['category']:
                    query['category'] = filters['category']

                if 'search' in filters and filters['search']:
                    query['name'] = {'$regex': filters['search'], '$options': 'i'}

                if 'expiring_soon' in filters and filters['expiring_soon']:
                    # Items expiring in next 7 days
                    from datetime import timedelta
                    next_week = datetime.utcnow() + timedelta(days=7)
                    query['expiry_date'] = {'$lte': next_week, '$gte': datetime.utcnow()}

            # Sort by updated_at descending
            items = list(self.collection.find(query).sort("updated_at", -1))

            # Convert ObjectId to string and rename _id to id
            for item in items:
                item['id'] = str(item['_id'])
                del item['_id']

            return items

        except Exception as e:
            logger.error(f"Error getting grocery items: {e}")
            return []

    def update(self, item_id: str, update_data: Dict[str, Any]) -> bool:
        """Update grocery item"""
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()

            # Convert date strings to datetime objects if needed
            if 'expiry_date' in update_data and isinstance(update_data['expiry_date'], str):
                update_data['expiry_date'] = datetime.fromisoformat(update_data['expiry_date'])

            if 'last_purchased' in update_data and isinstance(update_data['last_purchased'], str):
                update_data['last_purchased'] = datetime.fromisoformat(update_data['last_purchased'])

            result = self.collection.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"Updated grocery item: {item_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error updating grocery item {item_id}: {e}")
            return False

    def delete(self, item_id: str) -> bool:
        """Delete grocery item"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(item_id)})
            if result.deleted_count > 0:
                logger.info(f"Deleted grocery item: {item_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting grocery item {item_id}: {e}")
            return False

    def get_expiring_items(self, days: int = 7, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get items expiring within specified days"""
        try:
            from datetime import timedelta

            query = {
                'expiry_date': {
                    '$lte': datetime.utcnow() + timedelta(days=days),
                    '$gte': datetime.utcnow()
                }
            }

            if user_id:
                query['user_id'] = user_id

            items = list(self.collection.find(query).sort("expiry_date", 1))

            # Convert ObjectId to string and rename _id to id
            for item in items:
                item['id'] = str(item['_id'])
                del item['_id']

            return items

        except Exception as e:
            logger.error(f"Error getting expiring items: {e}")
            return []

    def get_low_stock_items(self, threshold: int = 5, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get items with low stock"""
        try:
            query = {'quantity': {'$lte': threshold}}

            if user_id:
                query['user_id'] = user_id

            items = list(self.collection.find(query).sort("quantity", 1))

            # Convert ObjectId to string and rename _id to id
            for item in items:
                item['id'] = str(item['_id'])
                del item['_id']

            return items

        except Exception as e:
            logger.error(f"Error getting low stock items: {e}")
            return []

    def get_categories_stats(self, user_id: Optional[str] = None) -> Dict[str, int]:
        """Get statistics by category"""
        try:
            pipeline = []

            # Add user filter if provided
            if user_id:
                pipeline.append({"$match": {"user_id": user_id}})

            # Group by category and count
            pipeline.extend([
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ])

            result = list(self.collection.aggregate(pipeline))

            # Convert to dictionary
            stats = {}
            for item in result:
                stats[item['_id']] = item['count']

            return stats

        except Exception as e:
            logger.error(f"Error getting category statistics: {e}")
            return {}

    def search_items(self, search_term: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search items by name, category, or brand"""
        try:
            query = {
                "$or": [
                    {"name": {"$regex": search_term, "$options": "i"}},
                    {"category": {"$regex": search_term, "$options": "i"}},
                    {"brand": {"$regex": search_term, "$options": "i"}},
                    {"notes": {"$regex": search_term, "$options": "i"}}
                ]
            }

            if user_id:
                query["user_id"] = user_id

            items = list(self.collection.find(query).sort("updated_at", -1))

            # Convert ObjectId to string and rename _id to id
            for item in items:
                item['id'] = str(item['_id'])
                del item['_id']

            return items

        except Exception as e:
            logger.error(f"Error searching items: {e}")
            return []


class AnalyticsModel:
    """Analytics and AI-powered insights for grocery data"""

    def __init__(self):
        self.db_connection = MongoDBConnection()
        self.grocery_collection = self.db_connection.get_collection('grocery_items')
        self.analytics_collection = self.db_connection.get_collection('analytics_data')

    def calculate_consumption_rate(self, item_name: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate consumption rate for an item"""
        try:
            query = {"name": {"$regex": f"^{item_name}$", "$options": "i"}}
            if user_id:
                query["user_id"] = user_id

            # Get purchase history
            purchases = list(self.grocery_collection.find(query).sort("last_purchased", -1))

            if len(purchases) < 2:
                return {"rate": 0, "prediction": None, "confidence": "low"}

            # Calculate average consumption rate
            total_days = 0
            intervals = []

            for i in range(len(purchases) - 1):
                if purchases[i].get('last_purchased') and purchases[i+1].get('last_purchased'):
                    delta = purchases[i]['last_purchased'] - purchases[i+1]['last_purchased']
                    intervals.append(delta.days)

            if intervals:
                avg_interval = sum(intervals) / len(intervals)

                # Predict next purchase date
                last_purchase = purchases[0].get('last_purchased')
                if last_purchase:
                    from datetime import timedelta
                    next_purchase = last_purchase + timedelta(days=avg_interval)

                    return {
                        "rate": round(avg_interval, 2),
                        "prediction": next_purchase,
                        "confidence": "high" if len(intervals) >= 3 else "medium"
                    }

            return {"rate": 0, "prediction": None, "confidence": "low"}

        except Exception as e:
            logger.error(f"Error calculating consumption rate: {e}")
            return {"rate": 0, "prediction": None, "confidence": "low"}

    def get_spending_analytics(self, user_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get spending analytics for the specified period"""
        try:
            from datetime import timedelta

            start_date = datetime.utcnow() - timedelta(days=days)

            query = {
                "last_purchased": {"$gte": start_date},
                "price": {"$exists": True, "$ne": None}
            }

            if user_id:
                query["user_id"] = user_id

            # Aggregate spending by category
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$category",
                    "total_spent": {"$sum": "$price"},
                    "item_count": {"$sum": 1},
                    "avg_price": {"$avg": "$price"}
                }},
                {"$sort": {"total_spent": -1}}
            ]

            category_spending = list(self.grocery_collection.aggregate(pipeline))

            # Convert _id to category_name for template compatibility
            for item in category_spending:
                item['category_name'] = item['_id']
                del item['_id']

            # Calculate total spending
            total_spent = sum(item["total_spent"] for item in category_spending)

            return {
                "total_spent": round(total_spent, 2),
                "category_breakdown": category_spending,
                "period_days": days,
                "avg_daily_spending": round(total_spent / days, 2) if days > 0 else 0
            }

        except Exception as e:
            logger.error(f"Error getting spending analytics: {e}")
            return {"total_spent": 0, "category_breakdown": [], "period_days": days, "avg_daily_spending": 0}
