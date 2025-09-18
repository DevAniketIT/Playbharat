from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid

User = get_user_model()


class Subscription(models.Model):
    """User subscriptions to channels"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    channel = models.ForeignKey('accounts.Channel', on_delete=models.CASCADE, related_name='subscribers')
    
    # Notification settings
    notify_all = models.BooleanField(default=True)
    notify_personalized = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('subscriber', 'channel')
        indexes = [
            models.Index(fields=['subscriber', 'created_at']),
            models.Index(fields=['channel', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.subscriber.username} -> {self.channel.name}"


class Like(models.Model):
    """Likes and dislikes for videos"""
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_reactions')
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'video')
        indexes = [
            models.Index(fields=['video', 'reaction_type']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.reaction_type}d {self.video.title}"


class Comment(models.Model):
    """Comments on videos with nested replies support"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField(max_length=1000)
    
    # Moderation
    is_edited = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    
    # Statistics
    like_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['video', 'parent', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.video.title}"
    
    @property
    def is_reply(self):
        return self.parent is not None
    
    def get_absolute_url(self):
        return f"{self.video.get_absolute_url()}#comment-{self.id}"


class CommentLike(models.Model):
    """Likes for comments"""
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_reactions')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'comment')
        indexes = [
            models.Index(fields=['comment', 'reaction_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.reaction_type}d comment"


class WatchHistory(models.Model):
    """User's video watch history"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='watch_records')
    
    # Watch details
    watch_duration = models.DurationField()  # How long they watched
    watch_percentage = models.FloatField()  # Percentage of video watched (0-100)
    completed = models.BooleanField(default=False)  # Watched >90% of video
    
    # Device and location info
    device_type = models.CharField(max_length=50, blank=True)  # desktop, mobile, tablet
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    watched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'video')  # One record per user per video
        ordering = ['-watched_at']
        indexes = [
            models.Index(fields=['user', 'watched_at']),
            models.Index(fields=['video', 'watched_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"


class Share(models.Model):
    """Video sharing records"""
    PLATFORM_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('email', 'Email'),
        ('copy_link', 'Copy Link'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares', null=True, blank=True)
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='shares')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    
    # Analytics
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['video', 'platform', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        user_name = self.user.username if self.user else 'Anonymous'
        return f"{user_name} shared {self.video.title} on {self.platform}"


class Report(models.Model):
    """Content reporting system"""
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('comment', 'Comment'),
        ('channel', 'Channel'),
    ]
    
    REASON_CHOICES = [
        ('spam', 'Spam or misleading'),
        ('harassment', 'Harassment or bullying'),
        ('hate_speech', 'Hate speech'),
        ('violence', 'Violence or dangerous content'),
        ('adult_content', 'Adult content'),
        ('copyright', 'Copyright violation'),
        ('privacy', 'Privacy violation'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    
    # Content being reported (generic relations would be better but keeping simple)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    channel = models.ForeignKey('accounts.Channel', on_delete=models.CASCADE, null=True, blank=True)
    
    # Report details
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(max_length=1000, blank=True)
    
    # Moderation
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_reports')
    moderator_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'status']),
            models.Index(fields=['reporter', 'created_at']),
        ]
    
    def __str__(self):
        return f"Report by {self.reporter.username} - {self.reason}"
