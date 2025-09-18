from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.db.models import F, Q
import json

from .models import Video, Playlist
from interactions.models import Comment
from interactions.forms import CommentForm
from interactions.models import Like, Follow


class VideoLikeAPIView(LoginRequiredMixin, View):
    """HTMX endpoint for liking/unliking videos"""
    
    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        
        # Check if user already liked the video
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type_id=video._meta.label,
            object_id=video.pk,
            defaults={'like_type': 'like'}
        )
        
        if not created:
            # Unlike if already liked
            like.delete()
            liked = False
            video.like_count = F('like_count') - 1
        else:
            # Like the video
            liked = True
            video.like_count = F('like_count') + 1
        
        video.save()
        video.refresh_from_db()
        
        # Return HTMX fragment
        html = render_to_string('videos/partials/like_button.html', {
            'video': video,
            'liked': liked,
            'user': request.user
        })
        
        return HttpResponse(html)


class VideoCommentAPIView(LoginRequiredMixin, View):
    """HTMX endpoint for adding comments"""
    
    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        
        if not video.allow_comments:
            return JsonResponse({'error': 'Comments disabled'}, status=403)
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.video = video
            comment.save()
            
            # Update comment count
            video.comment_count = F('comment_count') + 1
            video.save()
            
            # Return the new comment HTML
            html = render_to_string('videos/partials/comment.html', {
                'comment': comment,
                'user': request.user
            })
            
            return HttpResponse(html)
        
        return JsonResponse({'errors': form.errors}, status=400)


class LoadCommentsAPIView(View):
    """HTMX endpoint for loading more comments"""
    
    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        page = request.GET.get('page', 1)
        
        comments = video.comments.filter(
            is_approved=True,
            parent=None
        ).select_related('user').order_by('-created_at')
        
        paginator = Paginator(comments, 10)
        page_obj = paginator.get_page(page)
        
        html = render_to_string('videos/partials/comments_list.html', {
            'comments': page_obj,
            'video': video,
            'user': request.user
        })
        
        return HttpResponse(html)


class VideoSearchSuggestionsAPIView(View):
    """HTMX endpoint for search suggestions"""
    
    def get(self, request):
        query = request.GET.get('q', '')
        
        if len(query) < 2:
            return HttpResponse('')
        
        videos = Video.objects.filter(
            title__icontains=query,
            is_published=True,
            visibility='public'
        ).select_related('channel')[:8]
        
        html = render_to_string('videos/partials/search_suggestions.html', {
            'videos': videos,
            'query': query
        })
        
        return HttpResponse(html)


class PlaylistToggleAPIView(LoginRequiredMixin, View):
    """HTMX endpoint for adding/removing videos from playlists"""
    
    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        playlist_id = request.POST.get('playlist_id')
        
        if not playlist_id:
            return JsonResponse({'error': 'No playlist specified'}, status=400)
        
        playlist = get_object_or_404(
            Playlist, 
            pk=playlist_id, 
            user=request.user
        )
        
        if video in playlist.videos.all():
            playlist.videos.remove(video)
            action = 'removed'
        else:
            playlist.videos.add(video)
            action = 'added'
        
        html = render_to_string('videos/partials/playlist_button.html', {
            'video': video,
            'playlist': playlist,
            'action': action
        })
        
        return HttpResponse(html)


class ChannelSubscribeAPIView(LoginRequiredMixin, View):
    """HTMX endpoint for subscribing to channels"""
    
    def post(self, request, handle):
        from accounts.models import Channel
        
        channel = get_object_or_404(Channel, handle=handle)
        
        if channel.user == request.user:
            return JsonResponse({'error': 'Cannot subscribe to own channel'}, status=400)
        
        # Check if already following
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=channel.user
        )
        
        if not created:
            follow.delete()
            subscribed = False
            channel.subscriber_count = F('subscriber_count') - 1
        else:
            subscribed = True
            channel.subscriber_count = F('subscriber_count') + 1
        
        channel.save()
        channel.refresh_from_db()
        
        html = render_to_string('channels/partials/subscribe_button.html', {
            'channel': channel,
            'subscribed': subscribed,
            'user': request.user
        })
        
        return HttpResponse(html)


class VideoViewTrackingAPIView(View):
    """HTMX endpoint for tracking video views"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        
        # Only track view if not the owner
        if not request.user.is_authenticated or request.user != video.uploader:
            # In a production app, you'd want to track unique views
            # using sessions or IP addresses to prevent spam
            video.view_count = F('view_count') + 1
            video.save()
        
        return JsonResponse({'success': True, 'views': video.view_count})


class RelatedVideosAPIView(View):
    """HTMX endpoint for loading related videos"""
    
    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        
        # Get related videos from same channel or category
        related_videos = Video.objects.filter(
            Q(channel=video.channel) | Q(category=video.category),
            is_published=True,
            visibility='public'
        ).exclude(pk=video.pk)[:12]
        
        html = render_to_string('videos/partials/related_videos.html', {
            'videos': related_videos,
            'current_video': video
        })
        
        return HttpResponse(html)


class VideoUploadProgressAPIView(LoginRequiredMixin, View):
    """HTMX endpoint for upload progress"""
    
    def get(self, request):
        upload_id = request.GET.get('upload_id')
        
        # In a real implementation, you'd use Celery or similar
        # to track actual upload/processing progress
        
        # Mock progress for demonstration
        import random
        progress = {
            'upload_progress': random.randint(10, 100),
            'processing_progress': random.randint(0, 50),
            'status': 'uploading',
            'message': 'Processing your video...'
        }
        
        html = render_to_string('videos/partials/upload_progress.html', {
            'progress': progress,
            'upload_id': upload_id
        })
        
        return HttpResponse(html)


class TrendingVideosAPIView(View):
    """HTMX endpoint for loading trending videos"""
    
    def get(self, request):
        category = request.GET.get('category', '')
        timeframe = request.GET.get('timeframe', 'week')
        
        videos = Video.objects.filter(
            is_published=True,
            visibility='public'
        )
        
        if category:
            videos = videos.filter(category=category)
        
        # Sort by view count for trending
        videos = videos.order_by('-view_count', '-created_at')[:20]
        
        html = render_to_string('videos/partials/video_grid.html', {
            'videos': videos,
            'title': f'Trending {category.title()} Videos' if category else 'Trending Videos'
        })
        
        return HttpResponse(html)


class VideoRecommendationsAPIView(LoginRequiredMixin, View):
    """HTMX endpoint for personalized video recommendations"""
    
    def get(self, request):
        # Simple recommendation based on user's viewing history
        # In production, this would use ML algorithms
        
        # Get categories user has watched
        user_categories = Video.objects.filter(
            # This would be based on actual view history
            uploader=request.user  # Simplified for demo
        ).values_list('category', flat=True).distinct()
        
        recommended_videos = Video.objects.filter(
            category__in=user_categories,
            is_published=True,
            visibility='public'
        ).exclude(uploader=request.user).order_by('-view_count')[:16]
        
        html = render_to_string('videos/partials/video_grid.html', {
            'videos': recommended_videos,
            'title': 'Recommended for You'
        })
        
        return HttpResponse(html)