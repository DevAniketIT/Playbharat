"""
PlayBharat Admin Configuration
YouTube-like comprehensive admin system with full control
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path, include

# Import all admin components
try:
    from .admin_enhanced import (
        admin_site, EnhancedUserAdmin, EnhancedChannelAdmin, 
        EnhancedVideoAdmin, AdminActionAdmin, UserStrikeAdmin, 
        ContentFlagAdmin, UserSuspensionAdmin, ChannelSuspensionAdmin
    )
except ImportError:
    # Fallback if admin_enhanced is not available
    from django.contrib.admin import site as admin_site

from .models import Channel
try:
    from .admin_models import (
        AdminAction, UserStrike, ContentFlag, UserSuspension, ChannelSuspension
    )
except ImportError:
    # Admin models not available yet
    pass

# Get the User model
User = get_user_model()

# Profile model integrated into User model - no separate registration needed

# Fallback admin for User if enhanced admin not available
if not hasattr(admin_site, '_registry') or User not in admin_site._registry:
    @admin.register(User)
    class CustomUserAdmin(UserAdmin):
        """Enhanced admin interface for PlayBharat users"""
        list_display = ('username', 'email', 'first_name', 'last_name', 'is_creator', 'is_verified_creator', 
                       'preferred_language', 'country', 'state', 'city', 'is_staff', 'is_active', 'date_joined')
        list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_creator', 'is_verified_creator', 
                      'preferred_language', 'country', 'email_verified', 'phone_verified')
        search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
        ordering = ('-date_joined',)
        
        fieldsets = UserAdmin.fieldsets + (
            ('PlayBharat Profile', {
                'fields': ('phone_number', 'date_of_birth', 'profile_picture', 'bio', 'preferred_language')
            }),
            ('Location', {
                'fields': ('country', 'state', 'city')
            }),
            ('Verification & Status', {
                'fields': ('email_verified', 'phone_verified', 'is_creator', 'is_verified_creator')
            }),
            ('Privacy Settings', {
                'fields': ('show_email', 'show_phone')
            }),
        )
        
        def get_queryset(self, request):
            return super().get_queryset(request)

# Fallback admin for Channel if enhanced admin not available
if not hasattr(admin_site, '_registry') or Channel not in admin_site._registry:
    @admin.register(Channel)
    class ChannelAdmin(admin.ModelAdmin):
        """Enhanced admin interface for channels"""
        list_display = ('name', 'handle', 'user', 'category', 'subscriber_count', 'total_videos', 
                       'total_views', 'is_active', 'is_monetized', 'created_at')
        list_filter = ('category', 'is_active', 'is_monetized', 'created_at')
        search_fields = ('name', 'handle', 'user__username', 'user__email', 'description')
        ordering = ('-created_at',)
        readonly_fields = ('created_at', 'updated_at')
        
        fieldsets = (
            ('Basic Information', {
                'fields': ('user', 'name', 'handle', 'description', 'category')
            }),
            ('Media', {
                'fields': ('avatar', 'banner')
            }),
            ('Statistics', {
                'fields': ('subscriber_count', 'total_views', 'total_videos'),
                'description': 'These statistics are automatically updated based on channel activity.'
            }),
            ('Settings', {
                'fields': ('is_active', 'is_monetized', 'allow_comments')
            }),
            ('Social Links', {
                'fields': ('website_url', 'twitter_url', 'instagram_url', 'facebook_url'),
                'classes': ('collapse',)
            }),
            ('Timestamps', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )
        
        def get_queryset(self, request):
            return super().get_queryset(request).select_related('user')

# Custom admin URLs (if dashboard exists)
try:
    def get_admin_urls():
        """Get admin URLs including custom dashboard URLs"""
        from .admin_dashboard import urlpatterns as dashboard_urls
        
        urls = [
            path('dashboard/', include(dashboard_urls)),
        ]
        return urls

    # Add custom URLs to admin site
    admin_site.get_urls = lambda: get_admin_urls() + admin_site.__class__.get_urls(admin_site)
except ImportError:
    pass

# Set the default admin site to our custom one
admin.site = admin_site

# Admin site configuration
admin_site.site_header = "PlayBharat Admin Dashboard"
admin_site.site_title = "PlayBharat Admin"
admin_site.index_title = "Content Management & Moderation Center"

# Additional admin customizations
class PlayBharatAdminConfig:
    """Configuration class for PlayBharat admin system"""
    
    # Admin permissions
    ADMIN_PERMISSIONS = {
        'can_ban_users': 'accounts.can_ban_users',
        'can_suspend_users': 'accounts.can_suspend_users',
        'can_issue_strikes': 'accounts.can_issue_strikes',
        'can_manage_channels': 'accounts.can_manage_channels',
        'can_moderate_content': 'accounts.can_moderate_content',
        'can_view_analytics': 'accounts.can_view_analytics',
        'can_export_data': 'accounts.can_export_data',
    }
    
    # Strike system settings
    STRIKE_SETTINGS = {
        'max_strikes_before_ban': 3,
        'strike_expiry_days': 90,
        'warning_duration_days': 30,
        'temporary_suspension_days': 7,
    }
    
    # Content moderation settings
    MODERATION_SETTINGS = {
        'auto_flag_threshold': 5,
        'auto_hide_threshold': 10,
        'require_manual_review': True,
        'enable_ai_moderation': False,
    }
    
    # Dashboard settings
    DASHBOARD_SETTINGS = {
        'show_recent_actions': True,
        'recent_actions_limit': 20,
        'enable_real_time_updates': True,
        'analytics_retention_days': 365,
    }

# Initialize admin configuration
admin_config = PlayBharatAdminConfig()

# Custom admin index template context
def admin_index_context(request):
    """Add custom context to admin index page"""
    from django.db.models import Count
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    context = {}
    
    if request.user.is_staff:
        # Quick stats for admin index
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        context.update({
            'total_users': User.objects.count(),
            'new_users_week': User.objects.filter(date_joined__date__gte=week_ago).count(),
            'total_channels': Channel.objects.count(),
            'admin_config': admin_config,
        })
        
        # Add moderation stats if models exist
        try:
            context.update({
                'banned_users': User.objects.filter(is_banned=True).count(),
                'active_strikes': UserStrike.objects.filter(is_active=True).count(),
                'pending_flags': ContentFlag.objects.filter(status='pending').count(),
            })
        except:
            pass
    
    return context

# Hook into admin site
original_index = admin_site.index
def custom_index(request, extra_context=None):
    """Custom admin index with additional context"""
    extra_context = extra_context or {}
    extra_context.update(admin_index_context(request))
    return original_index(request, extra_context)

admin_site.index = custom_index

# Admin help text
ADMIN_HELP = {
    'user_management': """
    <h3>User Management</h3>
    <p>Comprehensive user control with ban, suspend, strike, and warning capabilities.</p>
    <ul>
        <li><strong>Ban:</strong> Permanently disable user account and suspend all channels</li>
        <li><strong>Suspend:</strong> Temporarily disable user account with automatic restoration</li>
        <li><strong>Strike:</strong> Issue violations that automatically apply consequences</li>
        <li><strong>Warning:</strong> Notify users of policy violations without immediate consequences</li>
    </ul>
    """,
    
    'content_moderation': """
    <h3>Content Moderation</h3>
    <p>Advanced content control and community management tools.</p>
    <ul>
        <li><strong>Video Control:</strong> Hide, delete, or flag inappropriate content</li>
        <li><strong>Channel Management:</strong> Suspend, verify, or manage monetization</li>
        <li><strong>Flag Review:</strong> Process user reports and take appropriate action</li>
        <li><strong>Bulk Operations:</strong> Manage multiple items simultaneously</li>
    </ul>
    """,
    
    'analytics': """
    <h3>Analytics & Reporting</h3>
    <p>Comprehensive platform analytics and detailed reporting.</p>
    <ul>
        <li><strong>User Analytics:</strong> Registration trends, activity patterns</li>
        <li><strong>Content Analytics:</strong> Upload patterns, engagement metrics</li>
        <li><strong>Moderation Analytics:</strong> Strike trends, flag patterns</li>
        <li><strong>Export Tools:</strong> CSV/JSON export for external analysis</li>
    </ul>
    """
}

# Make admin help available
admin_site.admin_help = ADMIN_HELP
