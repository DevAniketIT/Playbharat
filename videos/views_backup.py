from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import models
from .models import Video, Playlist, PlaylistVideo
from accounts.models import Channel


class VideoUploadView(LoginRequiredMixin, TemplateView):
    """Video upload view"""
    template_name = 'videos/upload.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'channel'):
            messages.error(request, 'Please create a channel first to upload videos.')
            return redirect('accounts:create_channel')
        return super().dispatch(request, *args, **kwargs)


class UploadSuccessView(LoginRequiredMixin, TemplateView):
    """Upload success view"""
    template_name = 'videos/upload_success.html'


class ManageVideosView(LoginRequiredMixin, ListView):
    """Manage user's videos"""
    model = Video
    template_name = 'videos/manage.html'
    context_object_name = 'videos'
    paginate_by = 20
    
    def get_queryset(self):
        if hasattr(self.request.user, 'channel'):
            return self.request.user.channel.videos.all().order_by('-uploaded_at')
        return Video.objects.none()
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'channel'):
            messages.error(request, 'Please create a channel first.')
            return redirect('accounts:create_channel')
        return super().dispatch(request, *args, **kwargs)


class EditVideoView(LoginRequiredMixin, UpdateView):
    """Edit video metadata"""
    model = Video
    fields = ['title', 'description', 'tags', 'category', 'thumbnail', 'visibility', 'age_restriction', 'allow_comments', 'allow_likes']
    template_name = 'videos/edit.html'
    success_url = reverse_lazy('videos:manage')
    
    def get_queryset(self):
        if hasattr(self.request.user, 'channel'):
            return self.request.user.channel.videos.all()
        return Video.objects.none()
    
    def form_valid(self, form):
        messages.success(self.request, 'Video updated successfully!')
        return super().form_valid(form)


class DeleteVideoView(LoginRequiredMixin, DeleteView):
    """Delete video"""
    model = Video
    template_name = 'videos/delete_confirm.html'
    success_url = reverse_lazy('videos:manage')
    
    def get_queryset(self):
        if hasattr(self.request.user, 'channel'):
            return self.request.user.channel.videos.all()
        return Video.objects.none()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Video deleted successfully!')
        return super().delete(request, *args, **kwargs)


class VideoDetailView(DetailView):
    """Video detail page (redirects to streaming app)"""
    model = Video
    
    def get(self, request, *args, **kwargs):
        video = self.get_object()
        return redirect('streaming:watch', slug=video.slug)


class PlaylistListView(LoginRequiredMixin, ListView):
    """User's playlists"""
    model = Playlist
    template_name = 'videos/playlists.html'
    context_object_name = 'playlists'
    paginate_by = 20
    
    def get_queryset(self):
        return self.request.user.playlists.all().order_by('-updated_at')


class CreatePlaylistView(LoginRequiredMixin, CreateView):
    """Create new playlist"""
    model = Playlist
    fields = ['title', 'description', 'visibility']
    template_name = 'videos/create_playlist.html'
    success_url = reverse_lazy('videos:playlist_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Playlist "{form.instance.title}" created successfully!')
        return super().form_valid(form)


class PlaylistDetailView(DetailView):
    """Playlist detail view"""
    model = Playlist
    template_name = 'videos/playlist_detail.html'
    context_object_name = 'playlist'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['playlist_videos'] = self.object.playlistvideo_set.all().order_by('position')
        return context


class EditPlaylistView(LoginRequiredMixin, UpdateView):
    """Edit playlist"""
    model = Playlist
    fields = ['title', 'description', 'visibility']
    template_name = 'videos/edit_playlist.html'
    
    def get_queryset(self):
        return self.request.user.playlists.all()
    
    def get_success_url(self):
        return reverse_lazy('videos:playlist_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Playlist updated successfully!')
        return super().form_valid(form)


class UploadProgressView(LoginRequiredMixin, TemplateView):
    """HTMX endpoint for upload progress"""
    
    def get(self, request):
        # Mock progress data - in real implementation, this would check actual upload progress
        progress = request.GET.get('progress', 0)
        return JsonResponse({
            'progress': min(int(progress) + 10, 100),
            'status': 'uploading' if int(progress) < 100 else 'completed'
        })


class AddToPlaylistView(LoginRequiredMixin, TemplateView):
    """HTMX endpoint to add video to playlist"""
    
    def post(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        playlist_id = request.POST.get('playlist_id')
        
        if playlist_id:
            playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
            
            # Check if video is already in playlist
            if not PlaylistVideo.objects.filter(playlist=playlist, video=video).exists():
                # Get the highest position in the playlist
                max_position = PlaylistVideo.objects.filter(playlist=playlist).aggregate(
                    max_pos=models.Max('position')
                )['max_pos'] or 0
                
                PlaylistVideo.objects.create(
                    playlist=playlist,
                    video=video,
                    position=max_position + 1
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Video added to "{playlist.title}"'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Video is already in this playlist'
                })
        
        return JsonResponse({
            'success': False,
            'message': 'Please select a playlist'
        })
