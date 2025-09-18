from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os

from .models import Video, Playlist
# from interactions.models import Comment  # Comment when interactions app is ready
from .forms import VideoUploadForm, VideoEditForm, PlaylistForm
# from interactions.forms import CommentForm  # Comment when interactions app is ready
from .utils import VideoProcessor, ImageProcessor, get_video_duration_display, generate_unique_filename
from accounts.models import Channel


class VideoUploadView(LoginRequiredMixin, View):
    """Handle video upload with processing"""
    
    def get(self, request):
        # Check if user has a channel
        try:
            channel = request.user.channel
        except Channel.DoesNotExist:
            messages.error(request, 'You need to create a channel before uploading videos.')
            return redirect('accounts:create_channel')
        
        form = VideoUploadForm()
        return render(request, 'videos/upload.html', {
            'form': form,
            'channel': channel
        })
    
    def post(self, request):
        try:
            channel = request.user.channel
        except Channel.DoesNotExist:
            messages.error(request, 'You need to create a channel before uploading videos.')
            return redirect('accounts:create_channel')
        
        form = VideoUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            video = form.save(commit=False)
            video.channel = channel
            
            # Process video file
            if 'video_file' in request.FILES:
                video_file = request.FILES['video_file']
                
                # Validate video file
                processor = VideoProcessor()
                validation_errors = processor.validate_video_file(video_file)
                
                if validation_errors:
                    for error in validation_errors:
                        form.add_error('video_file', error)
                    return render(request, 'videos/upload.html', {
                        'form': form,
                        'channel': channel
                    })
                
                # Generate unique filename
                original_name = video_file.name
                video_file.name = generate_unique_filename(original_name)
                
                # Get video metadata
                video_info = processor.get_video_info(video_file)
                if video_info:
                    video.duration = int(video_info.get('duration', 0))
                    video.file_size = video_info.get('size', video_file.size)
                
                # Save video first
                video.save()
                
                # Generate thumbnail if not provided
                if not video.thumbnail and video_file:
                    thumbnail_path = processor.generate_thumbnail(video_file)
                    if thumbnail_path:
                        video.thumbnail = thumbnail_path
                        video.save()
                
                messages.success(request, 'Video uploaded successfully! Processing may take a few minutes.')
                return redirect('videos:manage')
            
        return render(request, 'videos/upload.html', {
            'form': form,
            'channel': channel
        })


class ManageVideosView(LoginRequiredMixin, ListView):
    """List user's uploaded videos for management"""
    model = Video
    template_name = 'videos/manage.html'
    context_object_name = 'videos'
    paginate_by = 12
    
    def get_queryset(self):
        return Video.objects.filter(
            channel__user=self.request.user
        ).order_by('-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get statistics
        videos = self.get_queryset()
        context['total_videos'] = videos.count()
        context['total_views'] = sum(video.view_count for video in videos)
        context['published_videos'] = videos.filter(visibility='public').count()
        context['draft_videos'] = videos.filter(visibility='private').count()
        
        return context


class VideoDetailView(DetailView):
    """Display video watch page"""
    model = Video
    template_name = 'videos/watch.html'
    context_object_name = 'video'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        video = super().get_object()
        
        # Increment view count if not the owner
        if not self.request.user.is_authenticated or self.request.user != video.channel.user:
            Video.objects.filter(pk=video.pk).update(view_count=F('view_count') + 1)
            video.refresh_from_db()
        
        return video
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.get_object()
        
        # Get related videos
        context['related_videos'] = Video.objects.filter(
            channel=video.channel,
            visibility='public',
            processing_status='completed'
        ).exclude(pk=video.pk)[:6]
        
        # Get comments - disabled until Comment model is implemented
        # context['comments'] = video.comments.filter(
        #     is_approved=True,
        #     parent=None
        # ).select_related('user').order_by('-created_at')[:10]
        # 
        # context['comment_form'] = CommentForm()
        
        # Format duration
        if video.duration:
            # Convert DurationField to total seconds
            total_seconds = video.duration.total_seconds()
            context['duration_display'] = get_video_duration_display(total_seconds)
        
        return context


class VideoEditView(LoginRequiredMixin, UpdateView):
    """Edit video details"""
    model = Video
    form_class = VideoEditForm
    template_name = 'videos/edit.html'
    
    def get_queryset(self):
        # Only allow editing own videos
        return Video.objects.filter(channel__user=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, 'Video updated successfully!')
        return reverse_lazy('videos:manage')


# Basic views for existing URLs
class VideoListView(ListView):
    model = Video
    template_name = 'videos/list.html'
    context_object_name = 'videos'
    paginate_by = 12
    
    def get_queryset(self):
        return Video.objects.filter(visibility='public', processing_status='completed').order_by('-uploaded_at')


class VideoUpdateView(VideoEditView):
    pass


class VideoDeleteView(LoginRequiredMixin, DeleteView):
    model = Video
    template_name = 'videos/delete.html'
    success_url = reverse_lazy('videos:manage')
    
    def get_queryset(self):
        return Video.objects.filter(channel__user=self.request.user)


class PlaylistListView(LoginRequiredMixin, ListView):
    model = Playlist
    template_name = 'videos/playlists.html'
    context_object_name = 'playlists'
    
    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user).order_by('-created_at')


class CreatePlaylistView(LoginRequiredMixin, CreateView):
    model = Playlist
    form_class = PlaylistForm
    template_name = 'videos/create_playlist.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PlaylistDetailView(DetailView):
    model = Playlist
    template_name = 'videos/playlist_detail.html'
    context_object_name = 'playlist'


class PlaylistEditView(LoginRequiredMixin, UpdateView):
    model = Playlist
    form_class = PlaylistForm
    template_name = 'videos/edit_playlist.html'
    
    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)


class CommentListView(View):
    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        comments = video.comments.filter(is_approved=True).order_by('-created_at')[:10]
        
        comments_data = []
        for comment in comments:
            comments_data.append({
                'id': comment.id,
                'user': comment.user.username if comment.user else 'Anonymous',
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({'comments': comments_data})


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.video = video
            comment.save()
            
            return JsonResponse({'success': True, 'message': 'Comment added!'})
        
        return JsonResponse({'success': False, 'errors': form.errors})


# API Views
class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        # Mock implementation
        return JsonResponse({'success': True, 'liked': True})


class IncrementViewView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        video.view_count = F('view_count') + 1
        video.save()
        return JsonResponse({'success': True})


class TrendingVideosView(ListView):
    model = Video
    template_name = 'videos/trending.html'
    context_object_name = 'videos'
    paginate_by = 12
    
    def get_queryset(self):
        return Video.objects.filter(
            visibility='public',
            processing_status='completed'
        ).order_by('-view_count')[:20]


class CategoryVideosView(ListView):
    model = Video
    template_name = 'videos/category.html'
    context_object_name = 'videos'
    
    def get_queryset(self):
        category = self.kwargs.get('category')
        return Video.objects.filter(category=category, is_published=True).order_by('-created_at')


class RecentVideosView(ListView):
    model = Video
    template_name = 'videos/recent.html'
    context_object_name = 'videos'
    
    def get_queryset(self):
        return Video.objects.filter(is_published=True).order_by('-created_at')[:20]


class VideoSuggestionsView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        videos = Video.objects.filter(title__icontains=query, is_published=True)[:5]
        
        suggestions = [{'id': v.id, 'title': v.title} for v in videos]
        return JsonResponse({'suggestions': suggestions})


class UploadProgressView(View):
    def get(self, request):
        return JsonResponse({'progress': 50, 'status': 'uploading'})


class AddToPlaylistView(LoginRequiredMixin, View):
    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        # Mock implementation
        return JsonResponse({'success': True, 'message': 'Added to playlist!'})


class VideoLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        return JsonResponse({'success': True})


class VideoReportView(LoginRequiredMixin, View):
    def post(self, request, pk):
        return JsonResponse({'success': True, 'message': 'Report submitted'})


class VideoShareView(View):
    def post(self, request, pk):
        return JsonResponse({'success': True, 'share_url': f'/videos/{pk}/'})


# Additional required views for URLs
class WatchlistView(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'videos/watchlist.html'
    context_object_name = 'videos'
    
    def get_queryset(self):
        # Mock implementation - return empty for now
        return Video.objects.none()


class WatchHistoryView(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'videos/history.html'
    context_object_name = 'videos'
    
    def get_queryset(self):
        # Mock implementation - return empty for now
        return Video.objects.none()