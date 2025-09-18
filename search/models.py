from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class SearchHistory(models.Model):
    """User search history for personalization"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history', null=True, blank=True)
    query = models.CharField(max_length=200)
    
    # Results info
    results_count = models.PositiveIntegerField(default=0)
    clicked_result = models.ForeignKey('videos.Video', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Analytics
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['query', 'created_at']),
        ]
    
    def __str__(self):
        user_name = self.user.username if self.user else 'Anonymous'
        return f"{user_name} searched for '{self.query}'"


class TrendingTopic(models.Model):
    """Trending topics and hashtags"""
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('entertainment', 'Entertainment'),
        ('music', 'Music'),
        ('news', 'News'),
        ('sports', 'Sports'),
        ('politics', 'Politics'),
        ('technology', 'Technology'),
        ('regional', 'Regional'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=100, unique=True)
    hashtag = models.CharField(max_length=100, blank=True)  # #topic format
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    
    # Metrics
    search_count = models.PositiveIntegerField(default=0)
    video_count = models.PositiveIntegerField(default=0)
    engagement_score = models.FloatField(default=0.0)  # Calculated trending score
    
    # Geographic info
    region = models.CharField(max_length=50, default='India')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_promoted = models.BooleanField(default=False)  # Manually promoted topics
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-engagement_score', '-updated_at']
        indexes = [
            models.Index(fields=['category', 'is_active', 'engagement_score']),
            models.Index(fields=['region', 'is_active', 'updated_at']),
        ]
    
    def __str__(self):
        return f"#{self.topic} ({self.engagement_score:.1f})"


class RecommendedVideo(models.Model):
    """Personalized video recommendations for users"""
    RECOMMENDATION_TYPE_CHOICES = [
        ('trending', 'Trending'),
        ('personalized', 'Personalized'),
        ('channel_based', 'Based on Subscriptions'),
        ('category_based', 'Based on Category Preference'),
        ('collaborative', 'Users Also Watched'),
        ('regional', 'Regional Content'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='recommendations')
    
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPE_CHOICES)
    score = models.FloatField()  # Recommendation confidence score (0-1)
    
    # Interaction tracking
    shown_count = models.PositiveIntegerField(default=0)
    clicked = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)  # User dismissed this recommendation
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'video')
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'recommendation_type', 'score']),
            models.Index(fields=['video', 'created_at']),
        ]
    
    def __str__(self):
        return f"Recommend {self.video.title} to {self.user.username} ({self.score:.2f})"


class PopularSearch(models.Model):
    """Popular search queries aggregated data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.CharField(max_length=200, unique=True)
    
    # Metrics (updated periodically)
    search_count = models.PositiveIntegerField(default=0)
    daily_searches = models.PositiveIntegerField(default=0)
    weekly_searches = models.PositiveIntegerField(default=0)
    monthly_searches = models.PositiveIntegerField(default=0)
    
    # Growth metrics
    growth_rate = models.FloatField(default=0.0)  # Percentage growth
    is_trending = models.BooleanField(default=False)
    
    # Geographic distribution
    top_regions = models.JSONField(default=dict)  # {'region': count}
    
    # Language detection
    primary_language = models.CharField(max_length=10, default='en')
    
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-search_count']
        indexes = [
            models.Index(fields=['is_trending', 'search_count']),
            models.Index(fields=['primary_language', 'search_count']),
        ]
    
    def __str__(self):
        return f"'{self.query}' ({self.search_count} searches)"
