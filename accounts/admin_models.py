"""
PlayBharat Admin Models - Content Moderation and User Management
Comprehensive admin system for YouTube-like platform control
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class AdminAction(models.Model):
    """Track all admin actions for audit trail"""
    ACTION_TYPES = [
        ('user_ban', 'User Banned'),
        ('user_unban', 'User Unbanned'),
        ('user_delete', 'User Deleted'),
        ('user_restore', 'User Restored'),
        ('user_strike', 'User Strike Issued'),
        ('user_warning', 'User Warning Issued'),
        ('channel_delete', 'Channel Deleted'),
        ('channel_suspend', 'Channel Suspended'),
        ('channel_restore', 'Channel Restored'),
        ('video_delete', 'Video Deleted'),
        ('video_hide', 'Video Hidden'),
        ('video_restore', 'Video Restored'),
        ('password_reset', 'Password Reset'),
        ('role_change', 'Role Changed'),
        ('verification_grant', 'Verification Granted'),
        ('verification_revoke', 'Verification Revoked'),
        ('monetization_enable', 'Monetization Enabled'),
        ('monetization_disable', 'Monetization Disabled'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_actions')
    target_channel = models.ForeignKey('Channel', on_delete=models.SET_NULL, null=True, blank=True)
    target_video = models.ForeignKey('videos.Video', on_delete=models.SET_NULL, null=True, blank=True)
    
    reason = models.TextField()
    details = models.JSONField(default=dict, blank=True)  # Store additional action details
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.admin_user.username} - {self.get_action_type_display()} - {self.timestamp}"


class UserStrike(models.Model):
    """YouTube-like strike system for users"""
    STRIKE_TYPES = [
        ('content_violation', 'Content Policy Violation'),
        ('spam', 'Spam or Misleading Content'),
        ('harassment', 'Harassment or Bullying'),
        ('copyright', 'Copyright Infringement'),
        ('adult_content', 'Adult Content'),
        ('hate_speech', 'Hate Speech'),
        ('violence', 'Violence or Dangerous Content'),
        ('misinformation', 'Misinformation'),
        ('community_guidelines', 'Community Guidelines Violation'),
        ('other', 'Other Violation'),
    ]
    
    SEVERITY_LEVELS = [
        ('warning', 'Warning'),
        ('strike_1', 'First Strike'),
        ('strike_2', 'Second Strike'),
        ('strike_3', 'Third Strike (Final)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='strikes')
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_strikes')
    
    strike_type = models.CharField(max_length=30, choices=STRIKE_TYPES)
    severity = models.CharField(max_length=15, choices=SEVERITY_LEVELS)
    reason = models.TextField()
    details = models.TextField(blank=True)
    
    # Reference to the violating content
    related_video = models.ForeignKey('videos.Video', on_delete=models.SET_NULL, null=True, blank=True)
    related_channel = models.ForeignKey('Channel', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Strike status
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_strikes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Strike: {self.user.username} - {self.get_strike_type_display()} ({self.get_severity_display()})"
    
    def save(self, *args, **kwargs):
        # Set expiry date for strikes (strikes expire after 90 days)
        if not self.expires_at and self.severity != 'warning':
            self.expires_at = timezone.now() + timedelta(days=90)
        
        super().save(*args, **kwargs)
        
        # Auto-apply consequences based on strike count
        self.apply_strike_consequences()
    
    def apply_strike_consequences(self):
        """Apply automatic consequences based on strike count"""
        active_strikes = UserStrike.objects.filter(
            user=self.user, 
            is_active=True, 
            expires_at__gt=timezone.now()
        ).count()
        
        user = self.user
        
        if active_strikes == 1:
            # First strike - Warning
            user.is_warned = True
            user.warning_expires_at = timezone.now() + timedelta(days=30)
            
        elif active_strikes == 2:
            # Second strike - Temporary suspension
            user.is_suspended = True
            user.suspension_expires_at = timezone.now() + timedelta(days=7)
            user.can_upload = False
            
        elif active_strikes >= 3:
            # Third strike - Permanent ban
            user.is_banned = True
            user.ban_reason = f"Multiple strikes: {self.get_strike_type_display()}"
            user.banned_at = timezone.now()
            user.is_active = False
            user.can_upload = False
            
            # Disable all user's channels
            for channel in user.channels.all():
                channel.is_active = False
                channel.is_suspended = True
                channel.suspension_reason = "User permanently banned"
                channel.save()
        
        user.save()


class ContentFlag(models.Model):
    """Content flagging and reporting system"""
    FLAG_TYPES = [
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('violence', 'Violence'),
        ('adult_content', 'Adult Content'),
        ('copyright', 'Copyright Violation'),
        ('misinformation', 'Misinformation'),
        ('dangerous', 'Dangerous Content'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewing', 'Under Review'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
        ('escalated', 'Escalated'),
    ]
    
    # Who reported
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_flags')
    
    # What was reported
    flagged_video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, null=True, blank=True)
    flagged_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_flags')
    flagged_channel = models.ForeignKey('Channel', on_delete=models.CASCADE, null=True, blank=True)
    
    flag_type = models.CharField(max_length=20, choices=FLAG_TYPES)
    description = models.TextField()
    additional_info = models.TextField(blank=True)
    
    # Review information
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_flags')
    review_notes = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        target = self.flagged_video or self.flagged_user or self.flagged_channel
        return f"Flag: {self.get_flag_type_display()} - {target} by {self.reported_by.username}"


class UserSuspension(models.Model):
    """Track user suspensions and bans"""
    SUSPENSION_TYPES = [
        ('temporary', 'Temporary Suspension'),
        ('permanent', 'Permanent Ban'),
        ('shadow_ban', 'Shadow Ban'),
        ('upload_ban', 'Upload Ban'),
        ('comment_ban', 'Comment Ban'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suspensions')
    suspended_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_suspensions')
    
    suspension_type = models.CharField(max_length=20, choices=SUSPENSION_TYPES)
    reason = models.TextField()
    details = models.TextField(blank=True)
    
    # Suspension period
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)  # Null for permanent bans
    
    # Status
    is_active = models.BooleanField(default=True)
    lifted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lifted_suspensions')
    lifted_at = models.DateTimeField(null=True, blank=True)
    lift_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_suspension_type_display()}: {self.user.username}"
    
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def lift_suspension(self, lifted_by, reason=""):
        """Lift the suspension"""
        self.is_active = False
        self.lifted_by = lifted_by
        self.lifted_at = timezone.now()
        self.lift_reason = reason
        self.save()
        
        # Update user status
        user = self.user
        if self.suspension_type == 'permanent':
            user.is_banned = False
            user.is_active = True
        elif self.suspension_type == 'temporary':
            user.is_suspended = False
        elif self.suspension_type == 'upload_ban':
            user.can_upload = True
            
        user.save()


class ChannelSuspension(models.Model):
    """Track channel suspensions"""
    SUSPENSION_TYPES = [
        ('temporary', 'Temporary Suspension'),
        ('permanent', 'Permanent Suspension'),
        ('monetization_disabled', 'Monetization Disabled'),
        ('upload_disabled', 'Upload Disabled'),
    ]
    
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, related_name='suspensions')
    suspended_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='channel_suspensions_issued')
    
    suspension_type = models.CharField(max_length=25, choices=SUSPENSION_TYPES)
    reason = models.TextField()
    details = models.TextField(blank=True)
    
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    lifted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='channel_suspensions_lifted')
    lifted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Channel {self.get_suspension_type_display()}: {self.channel.name}"


# Add fields to User model for admin control
def add_admin_fields_to_user():
    """Add additional fields to User model for admin control"""
    # These fields would be added via migration
    additional_fields = {
        'is_banned': models.BooleanField(default=False),
        'ban_reason': models.TextField(blank=True),
        'banned_at': models.DateTimeField(null=True, blank=True),
        'banned_by': models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='users_banned'),
        
        'is_suspended': models.BooleanField(default=False),
        'suspension_expires_at': models.DateTimeField(null=True, blank=True),
        'suspension_reason': models.TextField(blank=True),
        
        'is_warned': models.BooleanField(default=False),
        'warning_expires_at': models.DateTimeField(null=True, blank=True),
        'warning_count': models.IntegerField(default=0),
        
        'can_upload': models.BooleanField(default=True),
        'can_comment': models.BooleanField(default=True),
        'can_like': models.BooleanField(default=True),
        
        'strike_count': models.IntegerField(default=0),
        'last_strike_date': models.DateTimeField(null=True, blank=True),
        
        'admin_notes': models.TextField(blank=True),
        'last_activity': models.DateTimeField(null=True, blank=True),
        
        'requires_manual_review': models.BooleanField(default=False),
        'review_reason': models.TextField(blank=True),
    }
    return additional_fields


# Add fields to Channel model for admin control  
def add_admin_fields_to_channel():
    """Add additional fields to Channel model for admin control"""
    additional_fields = {
        'is_suspended': models.BooleanField(default=False),
        'suspension_reason': models.TextField(blank=True),
        'suspended_by': models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='channels_suspended'),
        'suspended_at': models.DateTimeField(null=True, blank=True),
        'suspension_expires_at': models.DateTimeField(null=True, blank=True),
        
        'is_under_review': models.BooleanField(default=False),
        'review_reason': models.TextField(blank=True),
        'reviewer': models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='channels_reviewing'),
        
        'strike_count': models.IntegerField(default=0),
        'warning_count': models.IntegerField(default=0),
        
        'can_upload': models.BooleanField(default=True),
        'can_livestream': models.BooleanField(default=True),
        'can_monetize': models.BooleanField(default=False),
        
        'admin_notes': models.TextField(blank=True),
        'compliance_score': models.IntegerField(default=100),  # 0-100 compliance score
        
        'requires_manual_approval': models.BooleanField(default=False),
        'auto_moderation_enabled': models.BooleanField(default=True),
    }
    return additional_fields