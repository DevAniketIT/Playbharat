from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Subscription, Like, Comment, CommentLike, 
    WatchHistory, Share, Report
)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for channel subscriptions"""
    list_display = ('subscriber', 'channel', 'notify_all', 'notify_personalized', 'created_at')
    list_filter = ('notify_all', 'notify_personalized', 'created_at', 'channel__category')
    search_fields = ('subscriber__username', 'subscriber__email', 'channel__name', 'channel__handle')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subscriber', 'channel')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin interface for video likes/dislikes"""
    list_display = ('user', 'video', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at', 'video__category')
    search_fields = ('user__username', 'video__title', 'video__channel__name')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'video', 'video__channel')


class CommentLikeInline(admin.TabularInline):
    model = CommentLike
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Enhanced admin interface for comments"""
    list_display = ('user', 'video', 'content_preview', 'parent', 'like_count', 
                   'reply_count', 'is_pinned', 'is_hidden', 'created_at')
    list_filter = ('is_pinned', 'is_hidden', 'is_edited', 'created_at', 'video__category')
    search_fields = ('user__username', 'video__title', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'like_count', 'reply_count', 'created_at', 'updated_at')
    inlines = [CommentLikeInline]
    
    fieldsets = (
        ('Comment Details', {
            'fields': ('user', 'video', 'parent', 'content')
        }),
        ('Moderation', {
            'fields': ('is_pinned', 'is_hidden', 'is_edited')
        }),
        ('Statistics', {
            'fields': ('like_count', 'reply_count'),
            'description': 'These statistics are automatically updated.'
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content Preview"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'video', 'parent', 'video__channel'
        ).prefetch_related('replies')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """Admin interface for comment likes/dislikes"""
    list_display = ('user', 'comment_preview', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__username', 'comment__content', 'comment__user__username')
    ordering = ('-created_at',)
    
    def comment_preview(self, obj):
        return obj.comment.content[:30] + '...' if len(obj.comment.content) > 30 else obj.comment.content
    comment_preview.short_description = "Comment Preview"


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    """Admin interface for watch history"""
    list_display = ('user', 'video', 'watch_percentage', 'completed', 'device_type', 'watched_at')
    list_filter = ('completed', 'device_type', 'watched_at', 'video__category')
    search_fields = ('user__username', 'video__title', 'video__channel__name')
    ordering = ('-watched_at',)
    readonly_fields = ('id', 'ip_address', 'watched_at')
    
    fieldsets = (
        ('Watch Details', {
            'fields': ('user', 'video', 'watch_duration', 'watch_percentage', 'completed')
        }),
        ('Device Information', {
            'fields': ('device_type', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'watched_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    """Admin interface for video shares"""
    list_display = ('user', 'video', 'platform', 'created_at')
    list_filter = ('platform', 'created_at', 'video__category')
    search_fields = ('user__username', 'video__title', 'video__channel__name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'ip_address', 'created_at')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Enhanced admin interface for content reports"""
    list_display = ('reporter', 'content_type', 'reason', 'status', 'moderator', 'created_at')
    list_filter = ('content_type', 'reason', 'status', 'created_at')
    search_fields = ('reporter__username', 'description', 'moderator__username')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Report Details', {
            'fields': ('reporter', 'content_type', 'video', 'comment', 'channel')
        }),
        ('Report Information', {
            'fields': ('reason', 'description')
        }),
        ('Moderation', {
            'fields': ('status', 'moderator', 'moderator_notes')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'reporter', 'moderator', 'video', 'comment', 'channel'
        )
