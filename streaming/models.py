from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class VideoView(models.Model):
    """Individual video view records for analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='video_views')
    
    # View details
    session_id = models.CharField(max_length=100)  # Unique session identifier
    watch_time = models.DurationField()  # Total watch time in this session
    completion_percentage = models.FloatField(default=0.0)  # 0-100
    quality_watched = models.CharField(max_length=10, default='auto')
    
    # Technical details
    device_type = models.CharField(max_length=20, blank=True)  # mobile, desktop, tablet, tv
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    screen_resolution = models.CharField(max_length=20, blank=True)  # 1920x1080
    
    # Network and location
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    
    # Referrer info
    referrer = models.URLField(blank=True)  # Where they came from
    traffic_source = models.CharField(max_length=50, blank=True)  # search, social, direct, etc.
    
    # Engagement metrics
    liked = models.BooleanField(default=False)
    commented = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)
    subscribed_after = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['video', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['country', 'created_at']),
            models.Index(fields=['device_type', 'created_at']),
        ]
    
    def __str__(self):
        user_name = self.user.username if self.user else 'Anonymous'
        return f"{user_name} viewed {self.video.title}"


class VideoAnalytics(models.Model):
    """Daily aggregated analytics for videos"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    
    # View metrics
    views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    total_watch_time = models.DurationField(null=True, blank=True)
    average_view_duration = models.DurationField(null=True, blank=True)
    average_completion_rate = models.FloatField(default=0.0)  # 0-100
    
    # Engagement metrics
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    
    # Audience metrics
    new_subscribers = models.PositiveIntegerField(default=0)
    subscriber_views = models.PositiveIntegerField(default=0)
    non_subscriber_views = models.PositiveIntegerField(default=0)
    
    # Traffic sources
    direct_views = models.PositiveIntegerField(default=0)
    search_views = models.PositiveIntegerField(default=0)
    social_views = models.PositiveIntegerField(default=0)
    suggested_views = models.PositiveIntegerField(default=0)
    
    # Device breakdown
    mobile_views = models.PositiveIntegerField(default=0)
    desktop_views = models.PositiveIntegerField(default=0)
    tablet_views = models.PositiveIntegerField(default=0)
    tv_views = models.PositiveIntegerField(default=0)
    
    # Geographic data (top countries/regions stored as JSON)
    top_countries = models.JSONField(default=dict)  # {'IN': 1000, 'US': 500}
    top_regions = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('video', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['video', 'date']),
            models.Index(fields=['date', 'views']),
        ]
    
    def __str__(self):
        return f"{self.video.title} - {self.date} ({self.views} views)"


class ChannelAnalytics(models.Model):
    """Daily aggregated analytics for channels"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey('accounts.Channel', on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    
    # Channel metrics
    total_views = models.PositiveIntegerField(default=0)
    unique_viewers = models.PositiveIntegerField(default=0)
    total_watch_time = models.DurationField(null=True, blank=True)
    
    # Subscriber metrics
    subscribers_gained = models.IntegerField(default=0)  # Can be negative if lost
    subscribers_lost = models.PositiveIntegerField(default=0)
    total_subscribers = models.PositiveIntegerField(default=0)
    
    # Content metrics
    videos_published = models.PositiveIntegerField(default=0)
    total_videos = models.PositiveIntegerField(default=0)
    
    # Engagement
    total_likes = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    total_shares = models.PositiveIntegerField(default=0)
    
    # Revenue (for monetized channels)
    estimated_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ad_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('channel', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['channel', 'date']),
            models.Index(fields=['date', 'total_views']),
        ]
    
    def __str__(self):
        return f"{self.channel.name} - {self.date}"


class StreamingSession(models.Model):
    """Live streaming sessions (for future live streaming feature)"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey('accounts.Channel', on_delete=models.CASCADE, related_name='live_streams')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    
    # Stream details
    stream_key = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    
    # Timing
    scheduled_start = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Metrics
    peak_viewers = models.PositiveIntegerField(default=0)
    total_viewers = models.PositiveIntegerField(default=0)
    chat_messages = models.PositiveIntegerField(default=0)
    
    # Settings
    allow_chat = models.BooleanField(default=True)
    chat_slow_mode = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_start']
        indexes = [
            models.Index(fields=['channel', 'status']),
            models.Index(fields=['status', 'scheduled_start']),
        ]
    
    def __str__(self):
        return f"{self.channel.name} - {self.title} ({self.status})"
    
    @property
    def is_live(self):
        return self.status == 'live'
    
    @property
    def duration(self):
        if self.actual_start and self.ended_at:
            return self.ended_at - self.actual_start
        return None
