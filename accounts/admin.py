"""
Django Admin Configuration for Accounts App

This module configures the Django admin interface for user profiles and activity logs.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserActivityLog


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'profile_picture',
        'phone_number',
        'preferred_theme',
        'email_notifications',
        'expiry_reminder_days',
        'low_stock_notifications',
        'default_grocery_category',
        'items_per_page',
    )


class UserAdmin(BaseUserAdmin):
    """
    Extended User admin with profile inline
    """
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile
    """
    list_display = (
        'user',
        'preferred_theme',
        'email_notifications',
        'expiry_reminder_days',
        'created_at',
    )
    list_filter = (
        'preferred_theme',
        'email_notifications',
        'low_stock_notifications',
        'created_at',
    )
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'profile_picture', 'phone_number')
        }),
        ('Preferences', {
            'fields': ('preferred_theme', 'default_grocery_category', 'items_per_page')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'expiry_reminder_days', 'low_stock_notifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    """
    Admin interface for UserActivityLog
    """
    list_display = (
        'user',
        'action',
        'description',
        'ip_address',
        'timestamp',
    )
    list_filter = (
        'action',
        'timestamp',
    )
    search_fields = ('user__username', 'user__email', 'description', 'ip_address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'action', 'description')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )
    
    def has_add_permission(self, request):
        """
        Disable adding activity logs through admin
        """
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        Disable editing activity logs through admin
        """
        return False


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
