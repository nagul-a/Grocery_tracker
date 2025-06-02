"""
AI-Powered Features for Smart Grocery Tracker

This module contains AI-powered functionality including:
- Smart suggestions based on purchase history
- Meal planning and recipe suggestions
- Price comparison and optimization
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import json
from django.conf import settings

logger = logging.getLogger('grocery_app')


class SmartSuggestions:
    """AI-powered smart suggestions for grocery items"""

    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY

    def get_purchase_suggestions(self, user_history: List[Dict], current_inventory: List[Dict]) -> List[Dict]:
        """
        Generate smart purchase suggestions based on history and current inventory
        """
        try:
            suggestions = []

            # Analyze purchase frequency
            item_frequency = {}
            for item in user_history:
                name = item.get('name', '').lower()
                if name:
                    item_frequency[name] = item_frequency.get(name, 0) + 1

            # Suggest frequently purchased items not in current inventory
            current_items = {item.get('name', '').lower() for item in current_inventory}

            for item_name, frequency in sorted(item_frequency.items(), key=lambda x: x[1], reverse=True):
                if item_name not in current_items and frequency >= 3:
                    # Find the most recent purchase of this item for details
                    recent_item = None
                    for item in reversed(user_history):
                        if item.get('name', '').lower() == item_name:
                            recent_item = item
                            break

                    if recent_item:
                        suggestions.append({
                            'name': recent_item['name'],
                            'category': recent_item.get('category', 'Other'),
                            'reason': f'Frequently purchased ({frequency} times)',
                            'confidence': min(frequency * 20, 100),
                            'suggested_quantity': recent_item.get('quantity', 1),
                            'unit': recent_item.get('unit', 'pieces')
                        })

            # Suggest items running low
            for item in current_inventory:
                if item.get('quantity', 0) <= 2:
                    suggestions.append({
                        'name': item['name'],
                        'category': item.get('category', 'Other'),
                        'reason': 'Running low in stock',
                        'confidence': 90,
                        'suggested_quantity': item.get('quantity', 1) * 2,
                        'unit': item.get('unit', 'pieces')
                    })

            return suggestions[:10]  # Return top 10 suggestions

        except Exception as e:
            logger.error(f"Error generating purchase suggestions: {e}")
            return []

    def get_healthier_alternatives(self, item_name: str) -> List[Dict]:
        """
        Suggest healthier alternatives for a given item
        """
        try:
            # Simple rule-based alternatives (can be enhanced with AI)
            alternatives_map = {
                'white bread': [
                    {'name': 'Whole wheat bread', 'reason': 'Higher fiber content'},
                    {'name': 'Multigrain bread', 'reason': 'More nutrients'}
                ],
                'regular milk': [
                    {'name': 'Low-fat milk', 'reason': 'Lower calories'},
                    {'name': 'Almond milk', 'reason': 'Dairy-free option'}
                ],
                'potato chips': [
                    {'name': 'Baked chips', 'reason': 'Less oil and calories'},
                    {'name': 'Vegetable chips', 'reason': 'More nutrients'}
                ],
                'soda': [
                    {'name': 'Sparkling water', 'reason': 'No added sugar'},
                    {'name': 'Fresh fruit juice', 'reason': 'Natural vitamins'}
                ]
            }

            item_lower = item_name.lower()
            for key, alternatives in alternatives_map.items():
                if key in item_lower:
                    return alternatives

            return []

        except Exception as e:
            logger.error(f"Error getting healthier alternatives: {e}")
            return []



class MealPlanner:
    """AI-powered meal planning and recipe suggestions"""

    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY

    def suggest_meals(self, available_items: List[Dict], dietary_preferences: List[str] = None) -> List[Dict]:
        """
        Suggest meals based on available grocery items
        """
        try:
            if not available_items:
                return []

            # Extract item names
            item_names = [item.get('name', '') for item in available_items]

            # Simple rule-based meal suggestions (can be enhanced with AI)
            meal_suggestions = []

            # Check for common meal combinations
            if any('chicken' in item.lower() for item in item_names):
                if any('rice' in item.lower() for item in item_names):
                    meal_suggestions.append({
                        'name': 'Chicken Fried Rice',
                        'ingredients_available': ['chicken', 'rice'],
                        'missing_ingredients': ['soy sauce', 'vegetables'],
                        'difficulty': 'Easy',
                        'cook_time': '30 minutes'
                    })

            if any('pasta' in item.lower() for item in item_names):
                if any('tomato' in item.lower() for item in item_names):
                    meal_suggestions.append({
                        'name': 'Pasta with Tomato Sauce',
                        'ingredients_available': ['pasta', 'tomatoes'],
                        'missing_ingredients': ['garlic', 'herbs'],
                        'difficulty': 'Easy',
                        'cook_time': '20 minutes'
                    })

            if any('egg' in item.lower() for item in item_names):
                meal_suggestions.append({
                    'name': 'Scrambled Eggs',
                    'ingredients_available': ['eggs'],
                    'missing_ingredients': ['butter', 'salt'],
                    'difficulty': 'Very Easy',
                    'cook_time': '10 minutes'
                })

            return meal_suggestions

        except Exception as e:
            logger.error(f"Error suggesting meals: {e}")
            return []

    def get_recipe_details(self, meal_name: str) -> Dict[str, Any]:
        """
        Get detailed recipe for a specific meal
        """
        try:
            # Simple recipe database (can be enhanced with external APIs)
            recipes = {
                'chicken fried rice': {
                    'ingredients': [
                        '2 cups cooked rice',
                        '1 lb chicken breast, diced',
                        '2 eggs, beaten',
                        '2 tbsp soy sauce',
                        '1 cup mixed vegetables',
                        '2 tbsp oil'
                    ],
                    'instructions': [
                        'Heat oil in a large pan',
                        'Cook chicken until done, remove',
                        'Scramble eggs, remove',
                        'Add rice and vegetables, stir-fry',
                        'Add chicken and eggs back',
                        'Season with soy sauce'
                    ],
                    'prep_time': '15 minutes',
                    'cook_time': '15 minutes',
                    'servings': 4
                },
                'pasta with tomato sauce': {
                    'ingredients': [
                        '1 lb pasta',
                        '2 cans crushed tomatoes',
                        '3 cloves garlic, minced',
                        '1 onion, diced',
                        '2 tbsp olive oil',
                        'Salt and pepper to taste'
                    ],
                    'instructions': [
                        'Cook pasta according to package directions',
                        'Heat oil, sauté onion and garlic',
                        'Add tomatoes, simmer 20 minutes',
                        'Season with salt and pepper',
                        'Serve over pasta'
                    ],
                    'prep_time': '10 minutes',
                    'cook_time': '25 minutes',
                    'servings': 4
                }
            }

            return recipes.get(meal_name.lower(), {})

        except Exception as e:
            logger.error(f"Error getting recipe details: {e}")
            return {}


class PriceComparison:
    """Price comparison and optimization features"""

    def __init__(self):
        pass

    def compare_prices(self, item_name: str) -> List[Dict]:
        """
        Compare prices across different stores (mock implementation)
        """
        try:
            # Mock price data (in real implementation, this would call external APIs)
            mock_prices = [
                {
                    'store': 'SuperMart',
                    'price': 2.99,
                    'unit': 'per lb',
                    'availability': 'In Stock',
                    'rating': 4.2
                },
                {
                    'store': 'FreshMarket',
                    'price': 3.49,
                    'unit': 'per lb',
                    'availability': 'In Stock',
                    'rating': 4.5
                },
                {
                    'store': 'BudgetStore',
                    'price': 2.49,
                    'unit': 'per lb',
                    'availability': 'Limited Stock',
                    'rating': 3.8
                }
            ]

            return mock_prices

        except Exception as e:
            logger.error(f"Error comparing prices: {e}")
            return []

    def get_best_deals(self, shopping_list: List[Dict]) -> List[Dict]:
        """
        Find the best deals for items in shopping list
        """
        try:
            deals = []

            for item in shopping_list:
                prices = self.compare_prices(item.get('name', ''))
                if prices:
                    best_price = min(prices, key=lambda x: x['price'])
                    deals.append({
                        'item': item['name'],
                        'best_store': best_price['store'],
                        'best_price': best_price['price'],
                        'savings': max(p['price'] for p in prices) - best_price['price']
                    })

            return deals

        except Exception as e:
            logger.error(f"Error getting best deals: {e}")
            return []
