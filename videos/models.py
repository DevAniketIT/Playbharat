from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
import os
import uuid

User = get_user_model()


def video_upload_path(instance, filename):
    """Generate upload path for video files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('videos/uploads/', str(instance.channel.user.id), filename)


def thumbnail_upload_path(instance, filename):
    """Generate upload path for thumbnail files"""
    ext = filename.split('.')[-1]
    filename = f"thumb_{uuid.uuid4()}.{ext}"
    return os.path.join('videos/thumbnails/', str(instance.channel.user.id), filename)


class Video(models.Model):
    """Main Video model for PlayBharat"""
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('unlisted', 'Unlisted'),
        ('private', 'Private'),
        ('scheduled', 'Scheduled'),
    ]
    
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    CATEGORY_CHOICES = [
        ('entertainment', 'Entertainment'),
        ('music', 'Music'),
        ('education', 'Education'),
        ('news', 'News'),
        ('sports', 'Sports'),
        ('gaming', 'Gaming'),
        ('technology', 'Technology'),
        ('cooking', 'Cooking'),
        ('travel', 'Travel'),
        ('lifestyle', 'Lifestyle'),
        ('business', 'Business'),
        ('comedy', 'Comedy'),
        ('health', 'Health'),
        ('art', 'Art'),
        ('religion', 'Religion'),
        ('politics', 'Politics'),
        ('regional', 'Regional Content'),
    ]
    
    AGE_RESTRICTION_CHOICES = [
        ('all', 'All Ages'),
        ('13+', '13+'),
        ('18+', '18+'),
    ]
    
    # Basic info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey('accounts.Channel', on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(max_length=5000, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='entertainment')
    
    # Media files
    video_file = models.FileField(upload_to=video_upload_path)
    thumbnail = models.ImageField(upload_to=thumbnail_upload_path, blank=True, null=True)
    
    # Video metadata
    duration = models.DurationField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # in bytes
    resolution_width = models.PositiveIntegerField(null=True, blank=True)
    resolution_height = models.PositiveIntegerField(null=True, blank=True)
    fps = models.FloatField(null=True, blank=True)
    
    # Processing status
    processing_status = models.CharField(
        max_length=15,
        choices=PROCESSING_STATUS_CHOICES,
        default='pending'
    )
    processing_error = models.TextField(blank=True)
    
    # Visibility and settings
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    age_restriction = models.CharField(max_length=5, choices=AGE_RESTRICTION_CHOICES, default='all')
    allow_comments = models.BooleanField(default=True)
    allow_likes = models.BooleanField(default=True)
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    
    # Language and location
    language = models.CharField(max_length=10, default='en')
    location = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['visibility', 'processing_status']),
            models.Index(fields=['category', 'uploaded_at']),
            models.Index(fields=['channel', 'visibility']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:240] + f"-{str(self.id)[:8]}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('videos:watch', kwargs={'slug': self.slug})
    
    def get_tags_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    @property
    def is_processed(self):
        return self.processing_status == 'completed'
    
    @property
    def duration_formatted(self):
        """Format duration as HH:MM:SS or MM:SS"""
        if not self.duration:
            return "--:--"
        
        total_seconds = int(self.duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"


class VideoQuality(models.Model):
    """Different quality versions of a video"""
    QUALITY_CHOICES = [
        ('360p', '360p'),
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
        ('1440p', '1440p'),
        ('2160p', '2160p (4K)'),
    ]
    
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='qualities')
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()  # in bytes
    bitrate = models.PositiveIntegerField(null=True, blank=True)  # in kbps
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('video', 'quality')
        ordering = ['-quality']
    
    def __str__(self):
        return f"{self.video.title} - {self.quality}"


class Playlist(models.Model):
    """User-created playlists"""
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('unlisted', 'Unlisted'),
        ('private', 'Private'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=1000, blank=True)
    thumbnail = models.ImageField(upload_to='playlists/thumbnails/', blank=True, null=True)
    
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    videos = models.ManyToManyField(Video, through='PlaylistVideo', related_name='playlists')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('playlists:detail', kwargs={'pk': self.id})


class PlaylistVideo(models.Model):
    """Through model for Playlist-Video relationship with ordering"""
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('playlist', 'video')
        ordering = ['position']
    
    def __str__(self):
        return f"{self.playlist.title} - {self.video.title}"
