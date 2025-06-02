"""
User Profile and Authentication Models for Smart Grocery Tracker

This module extends Django's built-in User model with additional profile information
and integrates with MongoDB for user-specific data storage.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
try:
    import pymongo
    from smart_grocery_tracker.settings import MONGODB_SETTINGS
except ImportError:
    pymongo = None
    MONGODB_SETTINGS = {}
import logging

logger = logging.getLogger('grocery_app')


class UserProfile(models.Model):
    """
    Extended user profile model linked to Django's User model
    """
    
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
        ('auto', 'Auto (System)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        null=True, 
        blank=True,
        help_text="Profile picture (optional)"
    )
    phone_number = models.CharField(
        max_length=15, 
        blank=True,
        help_text="Phone number for notifications"
    )
    preferred_theme = models.CharField(
        max_length=10, 
        choices=THEME_CHOICES, 
        default='light',
        help_text="Preferred UI theme"
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text="Receive email notifications for expiring items"
    )
    expiry_reminder_days = models.IntegerField(
        default=3,
        help_text="Days before expiry to send reminders"
    )
    low_stock_notifications = models.BooleanField(
        default=True,
        help_text="Receive notifications for low stock items"
    )
    
    # User preferences
    default_grocery_category = models.CharField(
        max_length=50,
        default='Other',
        help_text="Default category for new items"
    )
    items_per_page = models.IntegerField(
        default=12,
        help_text="Number of items to display per page"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    def get_mongodb_user_id(self):
        """Get MongoDB user identifier"""
        return str(self.user.id)

    def get_initials(self):
        """Get user initials for avatar placeholder"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name[0]}{self.user.last_name[0]}".upper()
        elif self.user.first_name:
            return self.user.first_name[0].upper()
        else:
            return self.user.username[0].upper()

    def get_display_name(self):
        """Get the best display name for the user"""
        if self.user.first_name:
            return self.user.first_name
        return self.user.username

    def get_profile_picture_url(self):
        """Return profile picture URL or default"""
        if self.profile_picture:
            return self.profile_picture.url
        return None

    def get_account_settings_summary(self):
        """Get summary of account settings for profile display"""
        try:
            essential_settings = self.user.essentialsettings
            return {
                'theme': essential_settings.get_theme_display(),
                'currency': essential_settings.get_default_currency_display(),
                'email_notifications': essential_settings.email_notifications,
                'low_stock_threshold': essential_settings.low_stock_threshold,
                'expiry_warning_days': essential_settings.expiry_warning_days,
            }
        except:
            return {
                'theme': 'Light Mode',
                'currency': '₹ Indian Rupee',
                'email_notifications': True,
                'low_stock_threshold': 5,
                'expiry_warning_days': 3,
            }

    def get_user_statistics(self):
        """Get user statistics for profile display"""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculate account age
        account_age = (now - self.user.date_joined).days

        # Calculate profile completion
        profile_completion = self.get_profile_completion_percentage()

        # Placeholder statistics (will be updated when grocery models are available)
        stats = {
            'total_items': 0,
            'items_this_month': 0,
            'low_stock_items': 0,
            'expiring_soon': 0,
            'account_age_days': account_age,
            'profile_completion': profile_completion,
            'last_activity': self.updated_at,
        }

        return stats

    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields_to_check = [
            bool(self.user.first_name),
            bool(self.user.last_name),
            bool(self.user.email),
            bool(self.phone_number),
            bool(self.profile_picture),
        ]

        completed_fields = sum(fields_to_check)
        total_fields = len(fields_to_check)

        return int((completed_fields / total_fields) * 100)

    @property
    def profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = [
            self.user.first_name,
            self.user.last_name,
            self.user.email,
            self.phone_number,
            self.profile_picture
        ]
        completed = sum(1 for field in fields if field)
        return int((completed / len(fields)) * 100)

    def get_user_statistics(self):
        """Get user statistics for profile display"""
        from grocery_app.models import GroceryItem
        from datetime import datetime, timedelta

        now = datetime.now()
        current_month = now.replace(day=1)

        try:
            # Get total items
            total_items = GroceryItem.objects.filter(user=self.user).count()

            # Get items added this month
            items_this_month = GroceryItem.objects.filter(
                user=self.user,
                created_at__gte=current_month
            ).count()

            # Get low stock items (using default threshold of 5)
            low_stock_items = GroceryItem.objects.filter(
                user=self.user,
                quantity__lte=5
            ).count()

            # Get expiring items (next 7 days)
            expiring_soon = GroceryItem.objects.filter(
                user=self.user,
                expiry_date__lte=now + timedelta(days=7),
                expiry_date__gte=now
            ).count()

            return {
                'total_items': total_items,
                'items_this_month': items_this_month,
                'low_stock_items': low_stock_items,
                'expiring_soon': expiring_soon,
                'account_age_days': (now.date() - self.user.date_joined.date()).days,
                'profile_completion': self.profile_completion_percentage
            }
        except Exception as e:
            # Return default values if there's an error
            return {
                'total_items': 0,
                'items_this_month': 0,
                'low_stock_items': 0,
                'expiring_soon': 0,
                'account_age_days': (now.date() - self.user.date_joined.date()).days,
                'profile_completion': self.profile_completion_percentage
            }


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserProfile when User is created
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save UserProfile when User is saved
    """
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()


class MongoDBUserManager:
    """
    Manager class for user-specific MongoDB operations
    """
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection"""
        try:
            if pymongo and MONGODB_SETTINGS:
                connection_string = f"mongodb://{MONGODB_SETTINGS['host']}:{MONGODB_SETTINGS['port']}/"
                self.client = pymongo.MongoClient(connection_string)
                self.db = self.client[MONGODB_SETTINGS['db_name']]
                logger.info("MongoDB connection established for user operations")
            else:
                logger.warning("PyMongo not available or MongoDB settings not configured")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
    
    def create_user_collections(self, user_id):
        """
        Create user-specific collections and indexes
        """
        try:
            if not self.db:
                logger.warning("MongoDB not connected, skipping collection creation")
                return False

            # Create indexes for user-specific collections
            collections = [
                'grocery_items',
                'user_preferences',
                'activity_logs',
                'shared_lists'
            ]

            for collection_name in collections:
                collection = self.db[collection_name]
                # Create index on user_id for performance
                collection.create_index([("user_id", 1)])

            logger.info(f"Created MongoDB collections for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error creating user collections: {e}")
            return False
    
    def get_user_data_stats(self, user_id):
        """
        Get statistics about user's data
        """
        try:
            stats = {}
            
            # Count grocery items
            stats['total_items'] = self.db.grocery_items.count_documents({"user_id": user_id})
            
            # Count activity logs
            stats['total_activities'] = self.db.activity_logs.count_documents({"user_id": user_id})
            
            # Count shared lists
            stats['shared_lists'] = self.db.shared_lists.count_documents({"owner_id": user_id})
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user data stats: {e}")
            return {}
    
    def cleanup_user_data(self, user_id):
        """
        Clean up user data when account is deleted
        """
        try:
            collections = ['grocery_items', 'user_preferences', 'activity_logs', 'shared_lists']
            
            for collection_name in collections:
                result = self.db[collection_name].delete_many({"user_id": user_id})
                logger.info(f"Deleted {result.deleted_count} documents from {collection_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up user data: {e}")
            return False


class UserActivityLog(models.Model):
    """
    Model to track user activities for audit and analytics
    """
    
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('item_added', 'Item Added'),
        ('item_updated', 'Item Updated'),
        ('item_deleted', 'Item Deleted'),
        ('profile_updated', 'Profile Updated'),
        ('list_shared', 'List Shared'),
        ('export_data', 'Data Exported'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional data as JSON
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} at {self.timestamp}"


class EssentialSettings(models.Model):
    """Essential user settings - simplified and focused"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # ===== ESSENTIAL APPEARANCE =====
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Light Mode'),
            ('dark', 'Dark Mode')
        ],
        default='light',
        help_text='Choose your preferred theme'
    )

    # ===== ESSENTIAL GROCERY SETTINGS =====
    default_currency = models.CharField(
        max_length=10,
        choices=[
            ('INR', '₹ Indian Rupee'),
            ('USD', '$ US Dollar'),
            ('EUR', '€ Euro'),
            ('GBP', '£ British Pound')
        ],
        default='INR',
        help_text='Default currency for price display'
    )

    low_stock_threshold = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text='Alert when items fall below this quantity'
    )

    expiry_warning_days = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(14)],
        help_text='Days before expiry to show warnings'
    )

    # ===== ESSENTIAL NOTIFICATIONS =====
    email_notifications = models.BooleanField(
        default=True,
        help_text='Receive email notifications for important updates'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Essential Settings"
        verbose_name_plural = "Essential Settings"

    def __str__(self):
        return f"{self.user.username}'s Essential Settings"


# Signal to create essential settings when user is created
@receiver(post_save, sender=User)
def create_essential_settings(sender, instance, created, **kwargs):
    """Create EssentialSettings when User is created"""
    if created:
        EssentialSettings.objects.create(user=instance)
