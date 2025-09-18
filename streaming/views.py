from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from videos.models import Video
from .models import VideoView, StreamingSession


class WatchVideoView(DetailView):
    """Main video watching page"""
    model = Video
    template_name = 'streaming/watch.html'
    context_object_name = 'video'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.object
        
        # Get related videos
        context['related_videos'] = Video.objects.filter(
            category=video.category,
            visibility='public',
            processing_status='completed'
        ).exclude(id=video.id)[:10]
        
        # Get channel info
        context['channel'] = video.channel
        
        # Check if user is subscribed
        if self.request.user.is_authenticated:
            from interactions.models import Subscription
            context['is_subscribed'] = Subscription.objects.filter(
                subscriber=self.request.user,
                channel=video.channel
            ).exists()
        else:
            context['is_subscribed'] = False
        
        # Get video comments
        from interactions.models import Comment
        context['comments'] = Comment.objects.filter(
            video=video,
            parent=None,
            is_hidden=False
        ).order_by('-created_at')[:20]
        
        return context


class EmbedVideoView(DetailView):
    """Embedded video player"""
    model = Video
    template_name = 'streaming/embed.html'
    context_object_name = 'video'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class ServeVideoView(TemplateView):
    """Serve video files"""
    
    def get(self, request, video_id, quality):
        video = get_object_or_404(Video, id=video_id)
        
        # Check if video is accessible
        if video.visibility == 'private' and video.channel.user != request.user:
            raise Http404("Video not found")
        
        # In a real implementation, this would serve the actual video file
        # For now, we'll return a placeholder response
        return JsonResponse({
            'video_url': f'/media/videos/{video_id}/{quality}.mp4',
            'quality': quality,
            'duration': str(video.duration) if video.duration else None
        })


class ServeThumbnailView(TemplateView):
    """Serve video thumbnails"""
    
    def get(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)
        
        if video.thumbnail:
            # In a real implementation, this would serve the thumbnail file
            return JsonResponse({
                'thumbnail_url': video.thumbnail.url
            })
        else:
            return JsonResponse({
                'thumbnail_url': '/static/images/default-thumbnail.jpg'
            })


class TrackViewView(TemplateView):
    """HTMX endpoint to track video views"""
    
    def post(self, request):
        video_id = request.POST.get('video_id')
        if video_id:
            video = get_object_or_404(Video, id=video_id)
            
            # Create or update view record
            session_id = request.session.session_key or 'anonymous'
            
            view_record, created = VideoView.objects.get_or_create(
                video=video,
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                defaults={
                    'watch_time': 0,
                    'completion_percentage': 0.0,
                    'device_type': 'desktop',  # Could be detected from user agent
                    'ip_address': request.META.get('REMOTE_ADDR'),
                }
            )
            
            if created:
                # Increment view count on video
                video.view_count += 1
                video.save()
            
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False})


class TrackEngagementView(TemplateView):
    """HTMX endpoint to track engagement (likes, comments, etc.)"""
    
    def post(self, request):
        video_id = request.POST.get('video_id')
        engagement_type = request.POST.get('type')  # 'like', 'comment', 'share', etc.
        
        if video_id and engagement_type:
            video = get_object_or_404(Video, id=video_id)
            
            # Update engagement metrics
            session_id = request.session.session_key or 'anonymous'
            
            try:
                view_record = VideoView.objects.get(
                    video=video,
                    user=request.user if request.user.is_authenticated else None,
                    session_id=session_id
                )
                
                if engagement_type == 'like':
                    view_record.liked = True
                elif engagement_type == 'comment':
                    view_record.commented = True
                elif engagement_type == 'share':
                    view_record.shared = True
                elif engagement_type == 'subscribe':
                    view_record.subscribed_after = True
                
                view_record.save()
                
                return JsonResponse({'success': True})
            except VideoView.DoesNotExist:
                pass
        
        return JsonResponse({'success': False})


class LiveStreamView(DetailView):
    """Live streaming view (future feature)"""
    model = StreamingSession
    template_name = 'streaming/live.html'
    context_object_name = 'stream'
    
    def get_object(self):
        return get_object_or_404(StreamingSession, id=self.kwargs['stream_id'], status='live')


class LiveChatView(TemplateView):
    """Live chat for streaming (future feature)"""
    template_name = 'streaming/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stream'] = get_object_or_404(StreamingSession, id=self.kwargs['stream_id'])
        return context
