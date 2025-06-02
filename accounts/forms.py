"""
Authentication Forms for Smart Grocery Tracker

This module contains all forms related to user authentication, registration,
and profile management with proper validation and styling.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, EssentialSettings


class LoginForm(forms.Form):
    """
    Custom login form with remember me functionality
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )


class UserRegistrationForm(UserCreationForm):
    """
    Enhanced user registration form with additional fields
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'autocomplete': 'email',
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'autocomplete': 'given-name',
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name',
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes and placeholders to inherited fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
        })
        
        # Update help texts
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters.'
    
    def clean_email(self):
        """
        Validate that email is unique
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email
    
    def clean_username(self):
        """
        Validate username
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username
    
    def save(self, commit=True):
        """
        Save user with additional fields
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    User profile form for managing user preferences and information
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture',
            'phone_number',
            'preferred_theme',
            'email_notifications',
            'expiry_reminder_days',
            'low_stock_notifications',
            'default_grocery_category',
            'items_per_page',
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890',
                'pattern': r'[\+]?[0-9\s\-\(\)]+',
            }),
            'preferred_theme': forms.Select(attrs={
                'class': 'form-select',
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'expiry_reminder_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30',
            }),
            'low_stock_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'default_grocery_category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'items_per_page': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '6',
                'max': '50',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add grocery category choices
        from grocery_app.django_models import GroceryItem
        category_choices = [('', 'Select Category')] + list(GroceryItem.CATEGORY_CHOICES)
        self.fields['default_grocery_category'].choices = category_choices
        
        # Add help texts
        self.fields['profile_picture'].help_text = 'Upload a profile picture (optional)'
        self.fields['phone_number'].help_text = 'Phone number for SMS notifications (optional)'
        self.fields['expiry_reminder_days'].help_text = 'Days before expiry to send reminders'
        self.fields['items_per_page'].help_text = 'Number of items to display per page'
    
    def clean_phone_number(self):
        """
        Validate phone number format
        """
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove spaces, dashes, and parentheses
            cleaned_phone = ''.join(filter(str.isdigit, phone.replace('+', '')))
            if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
                raise ValidationError('Please enter a valid phone number.')
        return phone
    
    def clean_expiry_reminder_days(self):
        """
        Validate expiry reminder days
        """
        days = self.cleaned_data.get('expiry_reminder_days')
        if days and (days < 1 or days > 30):
            raise ValidationError('Reminder days must be between 1 and 30.')
        return days
    
    def clean_items_per_page(self):
        """
        Validate items per page
        """
        items = self.cleaned_data.get('items_per_page')
        if items and (items < 6 or items > 50):
            raise ValidationError('Items per page must be between 6 and 50.')
        return items


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating basic user information
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email',
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'given-name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'family-name',
            }),
        }
    
    def clean_email(self):
        """
        Validate that email is unique (excluding current user)
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('A user with this email already exists.')
        return email


class PasswordChangeForm(forms.Form):
    """
    Custom password change form
    """
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current Password',
            'autocomplete': 'current-password',
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password',
            'autocomplete': 'new-password',
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password',
            'autocomplete': 'new-password',
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        """
        Validate current password
        """
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError('Current password is incorrect.')
        return current_password
    
    def clean_new_password2(self):
        """
        Validate that passwords match
        """
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('The two password fields didn\'t match.')
            
            # Validate password strength
            validate_password(password2, self.user)
        
        return password2
    
    def save(self):
        """
        Save the new password
        """
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


# ===== ESSENTIAL SETTINGS FORM =====

class EssentialSettingsForm(forms.ModelForm):
    """Simplified essential settings form"""

    class Meta:
        model = EssentialSettings
        fields = [
            'theme', 'default_currency', 'low_stock_threshold',
            'expiry_warning_days', 'email_notifications'
        ]
        widgets = {
            'theme': forms.Select(attrs={
                'class': 'form-select',
                'id': 'theme-select'
            }),
            'default_currency': forms.Select(attrs={
                'class': 'form-select',
                'id': 'currency-select'
            }),
            'low_stock_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '50',
                'id': 'stock-threshold'
            }),
            'expiry_warning_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '14',
                'id': 'expiry-days'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'email-notifications'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text and labels
        self.fields['theme'].label = 'Theme Preference'
        self.fields['default_currency'].label = 'Default Currency'
        self.fields['low_stock_threshold'].label = 'Low Stock Alert Threshold'
        self.fields['expiry_warning_days'].label = 'Expiry Warning Days'
        self.fields['email_notifications'].label = 'Email Notifications'


# ===== COMPREHENSIVE PROFILE FORM =====

class ComprehensiveProfileForm(forms.ModelForm):
    """
    Comprehensive form for editing user profile and basic user information
    """
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )

    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 'phone_number', 'preferred_theme',
            'email_notifications', 'expiry_reminder_days', 'low_stock_notifications'
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'profile-picture-input'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 9876543210'
            }),
            'preferred_theme': forms.Select(attrs={
                'class': 'form-select'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'expiry_reminder_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30'
            }),
            'low_stock_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.user = user

        # Add help text and labels
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['email'].label = 'Email Address'
        self.fields['profile_picture'].label = 'Profile Picture'
        self.fields['phone_number'].label = 'Phone Number'
        self.fields['preferred_theme'].label = 'Preferred Theme'
        self.fields['email_notifications'].label = 'Email Notifications'
        self.fields['expiry_reminder_days'].label = 'Expiry Reminder Days'
        self.fields['low_stock_notifications'].label = 'Low Stock Notifications'

        # Add help text
        self.fields['profile_picture'].help_text = "Upload a profile picture (JPG, PNG, max 5MB)"
        self.fields['phone_number'].help_text = "Your phone number for notifications"
        self.fields['expiry_reminder_days'].help_text = "Days before expiry to send reminders"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = getattr(self, 'user', None)

        if email and User.objects.filter(email=email).exclude(pk=user.pk if user else None).exists():
            raise forms.ValidationError("This email address is already in use.")

        return email

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')

        if picture:
            # Check file size (5MB limit)
            if picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Profile picture must be smaller than 5MB.")

            # Check file type
            if not picture.content_type.startswith('image/'):
                raise forms.ValidationError("Please upload a valid image file.")

        return picture

    def save(self, commit=True):
        profile = super().save(commit=False)

        if commit:
            # Update User model fields
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()

            # Save profile
            profile.save()

        return profile
