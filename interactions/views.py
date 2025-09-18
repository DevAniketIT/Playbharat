from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from videos.models import Video
from .models import Comment, Like, Subscription, WatchHistory, Share, Report


class AddCommentView(LoginRequiredMixin, TemplateView):
    """HTMX endpoint to add comments"""
    
    def post(self, request):
        video_id = request.POST.get('video_id')
        content = request.POST.get('content', '').strip()
        
        if video_id and content:
            video = get_object_or_404(Video, id=video_id)
            
            comment = Comment.objects.create(
                user=request.user,
                video=video,
                content=content
            )
            
            # Update video comment count
            video.comment_count += 1
            video.save()
            
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': str(comment.id),
                    'content': comment.content,
                    'author': comment.user.get_full_name() or comment.user.username,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        
        return JsonResponse({'success': False, 'error': 'Invalid data'})


class ReplyCommentView(LoginRequiredMixin, TemplateView):
    """HTMX endpoint to reply to comments"""
    
    def post(self, request, pk):
        parent_comment = get_object_or_404(Comment, id=pk)
        content = request.POST.get('content', '').strip()
        
        if content:
            reply = Comment.objects.create(
                user=request.user,
                video=parent_comment.video,
                parent=parent_comment,
                content=content
            )
            
            # Update parent comment reply count
            parent_comment.reply_count += 1
            parent_comment.save()
            
            return JsonResponse({
                'success': True,
                'reply': {
                    'id': str(reply.id),
                    'content': reply.content,
                    'author': reply.user.get_full_name() or reply.user.username,
                    'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        
        return JsonResponse({'success': False, 'error': 'Invalid content'})


class EditCommentView(LoginRequiredMixin, TemplateView):
    """HTMX endpoint to edit comments"""
    
    def post(self, request, pk):
        comment = get_object_or_404(Comment, id=pk, user=request.user)
        content = request.POST.get('content', '').strip()
        
        if content:
            comment.content = content
            comment.is_edited = True
            comment.save()
            
            return JsonResponse({
                'success': True,
                'content': comment.content
            })
        
        return JsonResponse({'success': False, 'error': 'Invalid content'})


class DeleteCommentView(LoginRequiredMixin, TemplateView):
    """HTMX endpoint to delete comments"""
    
    def post(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)
        
        # Check if user can delete (owner or video owner)
        if comment.user == request.user or comment.video.channel.user == request.user:
            comment.delete()
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Permission denied'})


class LikeCommentView(LoginRequiredMixin, TemplateView):
    """HTMX endpoint to like/unlike comments"""
    
    def post(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)
        
        from .models import CommentLike
        
        like, created = CommentLike.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'reaction_type': 'like'}
        )
        
        if not created:
            like.delete()
            liked = False
            comment.like_count -= 1
        else:
            liked = True
            comment.like_count += 1
        
        comment.save()
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'like_count': comment.like_count
        })


class LikeVideoView(LoginRequiredMixin, TemplateView):
    """HTMX endpoint to like/dislike videos"""
    
    def post(self, request, pk):
        video = get_object_or_404(Video, id=pk)
        reaction_type = request.POST.get('type', 'like')  # 'like' or 'dislike'
        
        like, created = Like.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={'reaction_type': reaction_type}
        )
        
        if not created:
            if like.reaction_type == reaction_type:
                # Remove reaction
                like.delete()
                if reaction_type == 'like':
                    video.like_count -= 1
                else:
                    video.dislike_count -= 1
                reacted = False
            else:
                # Change reaction
                if like.reaction_type == 'like':
                    video.like_count -= 1
                    video.dislike_count += 1
                else:
                    video.dislike_count -= 1
                    video.like_count += 1
                like.reaction_type = reaction_type
                like.save()
                reacted = True
        else:
            # New reaction
            if reaction_type == 'like':
                video.like_count += 1
            else:
                video.dislike_count += 1
            reacted = True
        
        video.save()
        
        return JsonResponse({
            'success': True,
            'reacted': reacted,
            'reaction_type': reaction_type,
            'like_count': video.like_count,
            'dislike_count': video.dislike_count
        })


class ShareVideoView(TemplateView):
    """Track video shares"""
    
    def post(self, request, pk):
        video = get_object_or_404(Video, id=pk)
        platform = request.POST.get('platform', 'copy_link')
        
        Share.objects.create(
            user=request.user if request.user.is_authenticated else None,
            video=video,
            platform=platform,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return JsonResponse({'success': True})


class ReportVideoView(LoginRequiredMixin, TemplateView):
    """Report video content"""
    
    def post(self, request, pk):
        video = get_object_or_404(Video, id=pk)
        reason = request.POST.get('reason')
        description = request.POST.get('description', '')
        
        if reason:
            Report.objects.create(
                reporter=request.user,
                content_type='video',
                video=video,
                reason=reason,
                description=description
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Report submitted successfully. We will review it shortly.'
            })
        
        return JsonResponse({'success': False, 'error': 'Please select a reason'})


class SubscribeView(LoginRequiredMixin, TemplateView):
    """Subscribe to channel"""
    
    def post(self, request):
        channel_id = request.POST.get('channel_id')
        if channel_id:
            from accounts.models import Channel
            channel = get_object_or_404(Channel, id=channel_id)
            
            subscription, created = Subscription.objects.get_or_create(
                subscriber=request.user,
                channel=channel
            )
            
            if created:
                channel.subscriber_count += 1
                channel.save()
                subscribed = True
            else:
                subscription.delete()
                channel.subscriber_count -= 1
                channel.save()
                subscribed = False
            
            return JsonResponse({
                'success': True,
                'subscribed': subscribed,
                'subscriber_count': channel.subscriber_count
            })
        
        return JsonResponse({'success': False})


class UnsubscribeView(LoginRequiredMixin, TemplateView):
    """Unsubscribe from channel"""
    
    def post(self, request):
        channel_id = request.POST.get('channel_id')
        if channel_id:
            from accounts.models import Channel
            channel = get_object_or_404(Channel, id=channel_id)
            
            try:
                subscription = Subscription.objects.get(
                    subscriber=request.user,
                    channel=channel
                )
                subscription.delete()
                channel.subscriber_count -= 1
                channel.save()
                
                return JsonResponse({'success': True})
            except Subscription.DoesNotExist:
                pass
        
        return JsonResponse({'success': False})


class SubscriptionsView(LoginRequiredMixin, ListView):
    """User's subscriptions"""
    model = Subscription
    template_name = 'interactions/subscriptions.html'
    context_object_name = 'subscriptions'
    paginate_by = 20
    
    def get_queryset(self):
        return self.request.user.subscriptions.all().order_by('-created_at')


class WatchHistoryView(LoginRequiredMixin, ListView):
    """User's watch history"""
    model = WatchHistory
    template_name = 'interactions/watch_history.html'
    context_object_name = 'watch_history'
    paginate_by = 20
    
    def get_queryset(self):
        return self.request.user.watch_history.all().order_by('-watched_at')


class ClearHistoryView(LoginRequiredMixin, TemplateView):
    """Clear watch history"""
    
    def post(self, request):
        WatchHistory.objects.filter(user=request.user).delete()
        messages.success(request, 'Watch history cleared successfully!')
        return JsonResponse({'success': True})


class LikedVideosView(LoginRequiredMixin, ListView):
    """User's liked videos"""
    model = Like
    template_name = 'interactions/liked_videos.html'
    context_object_name = 'liked_videos'
    paginate_by = 20
    
    def get_queryset(self):
        return self.request.user.video_reactions.filter(reaction_type='like').order_by('-created_at')


class MyReportsView(LoginRequiredMixin, ListView):
    """User's reports"""
    model = Report
    template_name = 'interactions/my_reports.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        return self.request.user.reports.all().order_by('-created_at')


class ReportDetailView(LoginRequiredMixin, DetailView):
    """Report detail view"""
    model = Report
    template_name = 'interactions/report_detail.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return self.request.user.reports.all()
