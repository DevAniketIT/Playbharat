"""
PlayBharat Enhanced Admin Interface
Comprehensive YouTube-like admin control system
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db import transaction
from django.utils.html import format_html
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.db.models import Q, Count
from datetime import datetime, timedelta
import json

from .admin_models import (
    AdminAction, UserStrike, ContentFlag, UserSuspension, 
    ChannelSuspension
)
from .models import Channel, Profile
from videos.models import Video

User = get_user_model()

# Custom Admin Site
class PlayBharatAdminSite(admin.AdminSite):
    site_header = "PlayBharat Admin Dashboard"
    site_title = "PlayBharat Admin"
    index_title = "Content Management & Moderation Center"
    
    def get_app_list(self, request, app_label=None):
        """Customize admin index page layout"""
        app_list = super().get_app_list(request, app_label)
        
        # Reorder apps for better organization
        custom_order = [
            'User Management',
            'Content Moderation',
            'Channel Management', 
            'Video Management',
            'Reports & Analytics',
            'System Administration'
        ]
        
        return app_list

# Create custom admin site instance
admin_site = PlayBharatAdminSite(name='playbharat_admin')

class AdminActionInline(admin.TabularInline):
    model = AdminAction
    extra = 0
    readonly_fields = ('timestamp', 'admin_user', 'action_type', 'reason')
    can_delete = False

class UserStrikeInline(admin.TabularInline):
    model = UserStrike
    extra = 0
    readonly_fields = ('created_at', 'issued_by', 'strike_type', 'severity')
    fields = ('strike_type', 'severity', 'reason', 'is_active', 'expires_at')

class UserSuspensionInline(admin.TabularInline):
    model = UserSuspension
    extra = 0
    readonly_fields = ('created_at', 'suspended_by')
    fields = ('suspension_type', 'reason', 'starts_at', 'expires_at', 'is_active')

@admin.register(User, site=admin_site)
class EnhancedUserAdmin(BaseUserAdmin):
    """Enhanced User Admin with full control capabilities"""
    
    list_display = [
        'username', 'email', 'get_full_name', 'get_status_badges', 
        'strike_count', 'warning_count', 'last_login', 'date_joined',
        'get_admin_actions'
    ]
    
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'is_banned', 'is_suspended', 
        'is_warned', 'can_upload', 'can_comment', 'date_joined', 'last_login',
        'requires_manual_review'
    ]
    
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    readonly_fields = [
        'date_joined', 'last_login', 'last_activity', 'strike_count',
        'warning_count', 'banned_at', 'last_strike_date'
    ]
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Admin Control', {
            'fields': (
                'is_banned', 'ban_reason', 'banned_at', 'banned_by',
                'is_suspended', 'suspension_expires_at', 'suspension_reason',
                'is_warned', 'warning_expires_at', 'warning_count',
            )
        }),
        ('Permissions Control', {
            'fields': (
                'can_upload', 'can_comment', 'can_like',
                'requires_manual_review', 'review_reason'
            )
        }),
        ('Activity Tracking', {
            'fields': (
                'strike_count', 'last_strike_date', 'last_activity',
                'admin_notes'
            )
        }),
    )
    
    actions = [
        'ban_users', 'unban_users', 'suspend_users_temporary', 'suspend_users_permanent',
        'lift_suspensions', 'issue_warning', 'reset_strikes', 'disable_upload',
        'enable_upload', 'reset_password_bulk', 'mark_for_review'
    ]
    
    inlines = [UserStrikeInline, UserSuspensionInline, AdminActionInline]
    
    def get_status_badges(self, obj):
        """Display status badges for user"""
        badges = []
        
        if obj.is_banned:
            badges.append('<span style="background:red;color:white;padding:2px 5px;border-radius:3px;">BANNED</span>')
        elif obj.is_suspended:
            badges.append('<span style="background:orange;color:white;padding:2px 5px;border-radius:3px;">SUSPENDED</span>')
        elif obj.is_warned:
            badges.append('<span style="background:yellow;color:black;padding:2px 5px;border-radius:3px;">WARNED</span>')
        
        if not obj.can_upload:
            badges.append('<span style="background:purple;color:white;padding:2px 5px;border-radius:3px;">UPLOAD DISABLED</span>')
        
        if obj.requires_manual_review:
            badges.append('<span style="background:blue;color:white;padding:2px 5px;border-radius:3px;">UNDER REVIEW</span>')
            
        if obj.is_staff:
            badges.append('<span style="background:green;color:white;padding:2px 5px;border-radius:3px;">STAFF</span>')
            
        return format_html(' '.join(badges))
    get_status_badges.short_description = 'Status'
    
    def get_admin_actions(self, obj):
        """Quick admin action buttons"""
        actions = []
        
        if obj.is_banned:
            actions.append(f'<a href="{reverse("admin:unban_user", args=[obj.pk])}" class="button">Unban</a>')
        else:
            actions.append(f'<a href="{reverse("admin:ban_user", args=[obj.pk])}" class="button">Ban</a>')
            
        if obj.is_suspended:
            actions.append(f'<a href="{reverse("admin:lift_suspension", args=[obj.pk])}" class="button">Lift Suspension</a>')
        else:
            actions.append(f'<a href="{reverse("admin:suspend_user", args=[obj.pk])}" class="button">Suspend</a>')
            
        actions.append(f'<a href="{reverse("admin:issue_strike", args=[obj.pk])}" class="button">Issue Strike</a>')
        actions.append(f'<a href="{reverse("admin:reset_password", args=[obj.pk])}" class="button">Reset Password</a>')
        
        return format_html(' '.join(actions))
    get_admin_actions.short_description = 'Quick Actions'
    
    def get_urls(self):
        """Add custom admin URLs"""
        urls = super().get_urls()
        custom_urls = [
            path('ban-user/<int:user_id>/', self.ban_user_view, name='ban_user'),
            path('unban-user/<int:user_id>/', self.unban_user_view, name='unban_user'),
            path('suspend-user/<int:user_id>/', self.suspend_user_view, name='suspend_user'),
            path('lift-suspension/<int:user_id>/', self.lift_suspension_view, name='lift_suspension'),
            path('issue-strike/<int:user_id>/', self.issue_strike_view, name='issue_strike'),
            path('reset-password/<int:user_id>/', self.reset_password_view, name='reset_password'),
            path('bulk-actions/', self.bulk_actions_view, name='bulk_actions'),
        ]
        return custom_urls + urls
    
    def ban_user_view(self, request, user_id):
        """Ban user view"""
        user = User.objects.get(pk=user_id)
        
        if request.method == 'POST':
            reason = request.POST.get('reason', 'Admin action')
            
            with transaction.atomic():
                # Ban user
                user.is_banned = True
                user.is_active = False
                user.ban_reason = reason
                user.banned_at = timezone.now()
                user.banned_by = request.user
                user.save()
                
                # Suspend all user's channels
                for channel in user.channels.all():
                    ChannelSuspension.objects.create(
                        channel=channel,
                        suspended_by=request.user,
                        suspension_type='permanent',
                        reason=f"User banned: {reason}"
                    )
                
                # Log admin action
                AdminAction.objects.create(
                    admin_user=request.user,
                    action_type='user_ban',
                    target_user=user,
                    reason=reason,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
            messages.success(request, f'User {user.username} has been banned successfully.')
            return redirect('admin:accounts_user_changelist')
            
        return render(request, 'admin/ban_user.html', {'user': user})
    
    # Bulk Actions
    def ban_users(self, request, queryset):
        """Ban multiple users"""
        count = 0
        for user in queryset:
            if not user.is_banned:
                user.is_banned = True
                user.is_active = False
                user.ban_reason = "Bulk admin action"
                user.banned_at = timezone.now()
                user.banned_by = request.user
                user.save()
                
                AdminAction.objects.create(
                    admin_user=request.user,
                    action_type='user_ban',
                    target_user=user,
                    reason="Bulk admin action"
                )
                count += 1
                
        messages.success(request, f'{count} users have been banned.')
    ban_users.short_description = "Ban selected users"
    
    def unban_users(self, request, queryset):
        """Unban multiple users"""
        count = 0
        for user in queryset.filter(is_banned=True):
            user.is_banned = False
            user.is_active = True
            user.ban_reason = ""
            user.banned_at = None
            user.banned_by = None
            user.save()
            
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='user_unban',
                target_user=user,
                reason="Bulk admin action"
            )
            count += 1
            
        messages.success(request, f'{count} users have been unbanned.')
    unban_users.short_description = "Unban selected users"
    
    def suspend_users_temporary(self, request, queryset):
        """Temporarily suspend users for 7 days"""
        count = 0
        for user in queryset.filter(is_banned=False):
            user.is_suspended = True
            user.suspension_expires_at = timezone.now() + timedelta(days=7)
            user.suspension_reason = "Temporary suspension - Bulk admin action"
            user.save()
            
            UserSuspension.objects.create(
                user=user,
                suspended_by=request.user,
                suspension_type='temporary',
                reason="Bulk admin action",
                expires_at=timezone.now() + timedelta(days=7)
            )
            
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='user_suspend',
                target_user=user,
                reason="Temporary suspension - Bulk admin action"
            )
            count += 1
            
        messages.success(request, f'{count} users have been suspended for 7 days.')
    suspend_users_temporary.short_description = "Suspend selected users (7 days)"
    
    def reset_password_bulk(self, request, queryset):
        """Reset passwords for selected users"""
        count = 0
        for user in queryset:
            # Generate random password
            new_password = User.objects.make_random_password()
            user.set_password(new_password)
            user.save()
            
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='password_reset',
                target_user=user,
                reason="Bulk password reset",
                details={'new_password': new_password}  # In production, don't store passwords
            )
            count += 1
            
        messages.success(request, f'Passwords reset for {count} users.')
    reset_password_bulk.short_description = "Reset passwords for selected users"


@admin.register(Channel, site=admin_site)
class EnhancedChannelAdmin(admin.ModelAdmin):
    """Enhanced Channel Admin with full control"""
    
    list_display = [
        'name', 'owner', 'get_status_badges', 'subscriber_count', 
        'video_count', 'created_at', 'get_admin_actions'
    ]
    
    list_filter = [
        'is_active', 'is_verified', 'is_suspended', 'is_under_review',
        'can_upload', 'can_livestream', 'can_monetize', 'created_at',
        'requires_manual_approval'
    ]
    
    search_fields = ['name', 'description', 'owner__username', 'owner__email']
    
    readonly_fields = [
        'created_at', 'updated_at', 'subscriber_count', 'video_count',
        'compliance_score', 'strike_count', 'warning_count'
    ]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('name', 'owner', 'description', 'is_active')
        }),
        ('Status & Verification', {
            'fields': (
                'is_verified', 'is_suspended', 'suspension_reason',
                'suspended_by', 'suspended_at', 'suspension_expires_at'
            )
        }),
        ('Permissions', {
            'fields': (
                'can_upload', 'can_livestream', 'can_monetize',
                'requires_manual_approval', 'auto_moderation_enabled'
            )
        }),
        ('Moderation', {
            'fields': (
                'is_under_review', 'review_reason', 'reviewer',
                'strike_count', 'warning_count', 'compliance_score',
                'admin_notes'
            )
        }),
        ('Statistics', {
            'fields': ('subscriber_count', 'video_count', 'created_at', 'updated_at')
        }),
    ]
    
    actions = [
        'suspend_channels', 'restore_channels', 'disable_monetization',
        'enable_monetization', 'disable_uploads', 'enable_uploads',
        'verify_channels', 'unverify_channels', 'mark_for_review'
    ]
    
    def get_status_badges(self, obj):
        """Display status badges"""
        badges = []
        
        if obj.is_suspended:
            badges.append('<span style="background:red;color:white;padding:2px 5px;border-radius:3px;">SUSPENDED</span>')
        
        if obj.is_under_review:
            badges.append('<span style="background:orange;color:white;padding:2px 5px;border-radius:3px;">UNDER REVIEW</span>')
            
        if obj.is_verified:
            badges.append('<span style="background:blue;color:white;padding:2px 5px;border-radius:3px;">VERIFIED</span>')
            
        if not obj.can_upload:
            badges.append('<span style="background:purple;color:white;padding:2px 5px;border-radius:3px;">UPLOAD DISABLED</span>')
            
        if obj.can_monetize:
            badges.append('<span style="background:green;color:white;padding:2px 5px;border-radius:3px;">MONETIZED</span>')
        
        return format_html(' '.join(badges))
    get_status_badges.short_description = 'Status'
    
    def get_admin_actions(self, obj):
        """Quick admin action buttons"""
        actions = []
        
        if obj.is_suspended:
            actions.append(f'<a href="#" class="button">Restore</a>')
        else:
            actions.append(f'<a href="#" class="button">Suspend</a>')
            
        if obj.is_verified:
            actions.append(f'<a href="#" class="button">Remove Verification</a>')
        else:
            actions.append(f'<a href="#" class="button">Verify</a>')
            
        if obj.can_monetize:
            actions.append(f'<a href="#" class="button">Disable Monetization</a>')
        else:
            actions.append(f'<a href="#" class="button">Enable Monetization</a>')
        
        return format_html(' '.join(actions))
    get_admin_actions.short_description = 'Quick Actions'
    
    # Bulk Actions
    def suspend_channels(self, request, queryset):
        """Suspend selected channels"""
        count = 0
        for channel in queryset.filter(is_suspended=False):
            channel.is_suspended = True
            channel.suspension_reason = "Bulk admin action"
            channel.suspended_by = request.user
            channel.suspended_at = timezone.now()
            channel.save()
            
            ChannelSuspension.objects.create(
                channel=channel,
                suspended_by=request.user,
                suspension_type='temporary',
                reason="Bulk admin suspension"
            )
            
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='channel_suspend',
                target_channel=channel,
                reason="Bulk admin action"
            )
            count += 1
            
        messages.success(request, f'{count} channels have been suspended.')
    suspend_channels.short_description = "Suspend selected channels"


@admin.register(Video, site=admin_site)
class EnhancedVideoAdmin(admin.ModelAdmin):
    """Enhanced Video Admin with full control"""
    
    list_display = [
        'title', 'channel', 'get_status_badges', 'view_count', 
        'like_count', 'upload_date', 'get_admin_actions'
    ]
    
    list_filter = [
        'is_active', 'is_published', 'is_flagged', 'is_monetized',
        'requires_review', 'upload_date', 'category'
    ]
    
    search_fields = ['title', 'description', 'channel__name', 'tags']
    
    readonly_fields = [
        'upload_date', 'view_count', 'like_count', 'dislike_count',
        'comment_count', 'file_size', 'duration'
    ]
    
    fieldsets = [
        ('Video Information', {
            'fields': ('title', 'description', 'channel', 'category', 'tags')
        }),
        ('Status & Visibility', {
            'fields': (
                'is_active', 'is_published', 'is_flagged', 'is_monetized',
                'requires_review', 'review_notes'
            )
        }),
        ('Statistics', {
            'fields': (
                'view_count', 'like_count', 'dislike_count', 'comment_count',
                'upload_date', 'file_size', 'duration'
            )
        }),
    ]
    
    actions = [
        'hide_videos', 'restore_videos', 'flag_videos', 'unflag_videos',
        'disable_monetization_videos', 'enable_monetization_videos',
        'mark_for_review_videos', 'approve_videos'
    ]
    
    def get_status_badges(self, obj):
        """Display status badges"""
        badges = []
        
        if not obj.is_active:
            badges.append('<span style="background:red;color:white;padding:2px 5px;border-radius:3px;">HIDDEN</span>')
        elif not obj.is_published:
            badges.append('<span style="background:orange;color:white;padding:2px 5px;border-radius:3px;">UNPUBLISHED</span>')
            
        if obj.is_flagged:
            badges.append('<span style="background:red;color:white;padding:2px 5px;border-radius:3px;">FLAGGED</span>')
            
        if obj.requires_review:
            badges.append('<span style="background:yellow;color:black;padding:2px 5px;border-radius:3px;">NEEDS REVIEW</span>')
            
        if obj.is_monetized:
            badges.append('<span style="background:green;color:white;padding:2px 5px;border-radius:3px;">MONETIZED</span>')
        
        return format_html(' '.join(badges))
    get_status_badges.short_description = 'Status'
    
    def get_admin_actions(self, obj):
        """Quick admin action buttons"""
        actions = []
        
        if obj.is_active:
            actions.append(f'<a href="#" class="button">Hide</a>')
        else:
            actions.append(f'<a href="#" class="button">Restore</a>')
            
        if obj.is_flagged:
            actions.append(f'<a href="#" class="button">Unflag</a>')
        else:
            actions.append(f'<a href="#" class="button">Flag</a>')
            
        actions.append(f'<a href="#" class="button">Delete</a>')
        
        return format_html(' '.join(actions))
    get_admin_actions.short_description = 'Quick Actions'
    
    # Bulk Actions
    def hide_videos(self, request, queryset):
        """Hide selected videos"""
        count = queryset.update(is_active=False)
        
        # Log actions
        for video in queryset:
            AdminAction.objects.create(
                admin_user=request.user,
                action_type='video_hide',
                target_video=video,
                reason="Bulk admin action"
            )
            
        messages.success(request, f'{count} videos have been hidden.')
    hide_videos.short_description = "Hide selected videos"


# Register admin models
@admin.register(AdminAction, site=admin_site)
class AdminActionAdmin(admin.ModelAdmin):
    list_display = ['admin_user', 'action_type', 'target_user', 'target_channel', 'target_video', 'timestamp']
    list_filter = ['action_type', 'timestamp', 'admin_user']
    search_fields = ['admin_user__username', 'reason', 'target_user__username']
    readonly_fields = ['timestamp', 'ip_address']
    date_hierarchy = 'timestamp'


@admin.register(UserStrike, site=admin_site)
class UserStrikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'strike_type', 'severity', 'issued_by', 'is_active', 'created_at', 'expires_at']
    list_filter = ['strike_type', 'severity', 'is_active', 'created_at']
    search_fields = ['user__username', 'reason', 'issued_by__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(ContentFlag, site=admin_site)
class ContentFlagAdmin(admin.ModelAdmin):
    list_display = ['get_flagged_content', 'flag_type', 'reported_by', 'status', 'created_at']
    list_filter = ['flag_type', 'status', 'created_at']
    search_fields = ['description', 'reported_by__username']
    readonly_fields = ['created_at', 'reviewed_at']
    
    def get_flagged_content(self, obj):
        if obj.flagged_video:
            return f"Video: {obj.flagged_video.title}"
        elif obj.flagged_user:
            return f"User: {obj.flagged_user.username}"
        elif obj.flagged_channel:
            return f"Channel: {obj.flagged_channel.name}"
        return "Unknown"
    get_flagged_content.short_description = 'Flagged Content'


@admin.register(UserSuspension, site=admin_site)
class UserSuspensionAdmin(admin.ModelAdmin):
    list_display = ['user', 'suspension_type', 'suspended_by', 'starts_at', 'expires_at', 'is_active']
    list_filter = ['suspension_type', 'is_active', 'starts_at']
    search_fields = ['user__username', 'reason', 'suspended_by__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'starts_at'


@admin.register(ChannelSuspension, site=admin_site)
class ChannelSuspensionAdmin(admin.ModelAdmin):
    list_display = ['channel', 'suspension_type', 'suspended_by', 'starts_at', 'expires_at', 'is_active']
    list_filter = ['suspension_type', 'is_active', 'starts_at']
    search_fields = ['channel__name', 'reason', 'suspended_by__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'starts_at'


# Replace default admin site
admin.site = admin_site