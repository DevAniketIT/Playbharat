from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Video, VideoQuality, Playlist, PlaylistVideo


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Enhanced admin interface for videos"""
    list_display = ('title', 'channel', 'category', 'visibility', 'processing_status', 
                   'view_count', 'like_count', 'comment_count', 'uploaded_at')
    list_filter = ('category', 'visibility', 'processing_status', 'age_restriction', 
                  'language', 'uploaded_at', 'allow_comments', 'allow_likes')
    search_fields = ('title', 'description', 'tags', 'channel__name', 'channel__user__username')
    ordering = ('-uploaded_at',)
    readonly_fields = ('id', 'uploaded_at', 'updated_at', 'view_count', 'like_count', 
                      'dislike_count', 'comment_count', 'duration_formatted', 'thumbnail_preview')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('channel', 'title', 'slug', 'description', 'category', 'tags')
        }),
        ('Media Files', {
            'fields': ('video_file', 'thumbnail', 'thumbnail_preview')
        }),
        ('Video Metadata', {
            'fields': ('duration', 'duration_formatted', 'file_size', 'resolution_width', 
                      'resolution_height', 'fps'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('processing_status', 'processing_error')
        }),
        ('Settings', {
            'fields': ('visibility', 'age_restriction', 'allow_comments', 'allow_likes')
        }),
        ('Statistics', {
            'fields': ('view_count', 'like_count', 'dislike_count', 'comment_count'),
            'description': 'These statistics are automatically updated based on user interactions.'
        }),
        ('Location & Language', {
            'fields': ('language', 'location'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'uploaded_at', 'published_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="150" height="auto" />',
                obj.thumbnail.url
            )
        return "No thumbnail"
    thumbnail_preview.short_description = "Thumbnail Preview"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('channel', 'channel__user')


@admin.register(VideoQuality)
class VideoQualityAdmin(admin.ModelAdmin):
    """Admin interface for video quality versions"""
    list_display = ('video', 'quality', 'file_size_mb', 'bitrate', 'created_at')
    list_filter = ('quality', 'created_at')
    search_fields = ('video__title', 'video__channel__name')
    ordering = ('-created_at',)
    
    def file_size_mb(self, obj):
        if obj.file_size:
            return f"{obj.file_size / (1024 * 1024):.2f} MB"
        return "Unknown"
    file_size_mb.short_description = "File Size (MB)"


class PlaylistVideoInline(admin.TabularInline):
    model = PlaylistVideo
    extra = 1
    ordering = ['position']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    """Admin interface for playlists"""
    list_display = ('title', 'user', 'visibility', 'video_count', 'created_at', 'updated_at')
    list_filter = ('visibility', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'user__username', 'user__email')
    ordering = ('-updated_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'video_count')
    inlines = [PlaylistVideoInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'visibility')
        }),
        ('Media', {
            'fields': ('thumbnail',)
        }),
        ('Statistics', {
            'fields': ('video_count',),
            'description': 'Number of videos in this playlist.'
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def video_count(self, obj):
        return obj.videos.count()
    video_count.short_description = "Video Count"
