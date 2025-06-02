"""
URL Configuration for Grocery App

This module defines all the URL patterns for the grocery tracking application.
"""

from django.urls import path
from . import views, mongodb_views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # MongoDB-based grocery list (NEW)
    path('mongodb/', mongodb_views.grocery_list_mongodb, name='grocery_list_mongodb'),
    path('mongodb/add/', mongodb_views.add_item_mongodb, name='add_item_mongodb'),
    path('mongodb/update/<str:item_id>/', mongodb_views.update_item_mongodb, name='update_item_mongodb'),
    path('mongodb/delete/<str:item_id>/', mongodb_views.delete_item_mongodb, name='delete_item_mongodb'),
    path('mongodb/get/<str:item_id>/', mongodb_views.get_item_mongodb, name='get_item_mongodb'),
    path('mongodb/search/', mongodb_views.search_items_mongodb, name='search_items_mongodb'),
    path('mongodb/analytics/', mongodb_views.analytics_mongodb, name='analytics_mongodb'),

    # CRUD operations (Original SQLite)
    path('add/', views.add_item, name='add_item'),
    path('edit/<str:item_id>/', views.edit_item, name='edit_item'),
    path('delete/<str:item_id>/', views.delete_item, name='delete_item'),

    # API endpoints
    path('api/search/', views.api_search_items, name='api_search'),
    path('api/suggestions/', views.api_get_suggestions, name='api_suggestions'),

    path('api/analytics/', views.api_analytics, name='api_analytics'),
    path('api/spending-analytics/', views.api_spending_analytics, name='api_spending_analytics'),
    path('api/meal-suggestions/', views.api_meal_suggestions, name='api_meal_suggestions'),
    path('api/price-comparison/', views.api_price_comparison, name='api_price_comparison'),

    # Interactive API endpoints
    path('api/quick-edit/<str:item_id>/', views.api_quick_edit, name='api_quick_edit'),
    path('api/quick-delete/<str:item_id>/', views.api_quick_delete, name='api_quick_delete'),
    path('api/bulk-actions/', views.api_bulk_actions, name='api_bulk_actions'),
    path('api/mark-purchased/<str:item_id>/', views.api_mark_purchased, name='api_mark_purchased'),
    path('api/shopping-list/', views.api_shopping_list, name='api_shopping_list'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),

    # AI-powered features
    path('meal-planner/', views.meal_planner, name='meal_planner'),
    path('price-comparison/', views.price_comparison, name='price_comparison'),
    path('smart-suggestions/', views.smart_suggestions, name='smart_suggestions'),

    # Analytics and reports
    path('analytics/', views.analytics, name='analytics'),
    path('reports/', views.reports, name='reports'),
    path('sustainability/', views.sustainability, name='sustainability'),
    path('status/', views.status, name='status'),
]
