from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .decorators import superuser_required
from accounts.models import User, Channel
from videos.models import Video, Playlist
from datetime import timedelta

User = get_user_model()


@superuser_required
def dashboard(request):
    """Main admin dashboard with statistics and overview"""
    
    # Basic statistics
    total_users = User.objects.count()
    total_channels = Channel.objects.count()
    total_videos = Video.objects.count()
    total_playlists = Playlist.objects.count()
    
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_videos = Video.objects.order_by('-uploaded_at')[:10]
    recent_channels = Channel.objects.order_by('-created_at')[:10]
    
    # Growth statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    users_this_week = User.objects.filter(date_joined__date__gte=week_ago).count()
    videos_this_week = Video.objects.filter(uploaded_at__date__gte=week_ago).count()
    channels_this_week = Channel.objects.filter(created_at__date__gte=week_ago).count()
    
    users_this_month = User.objects.filter(date_joined__date__gte=month_ago).count()
    videos_this_month = Video.objects.filter(uploaded_at__date__gte=month_ago).count()
    channels_this_month = Channel.objects.filter(created_at__date__gte=month_ago).count()
    
    # Top performing content
    top_videos = Video.objects.order_by('-view_count')[:5]
    top_channels = Channel.objects.order_by('-subscriber_count')[:5]
    
    context = {
        'total_users': total_users,
        'total_channels': total_channels,
        'total_videos': total_videos,
        'total_playlists': total_playlists,
        'recent_users': recent_users,
        'recent_videos': recent_videos,
        'recent_channels': recent_channels,
        'users_this_week': users_this_week,
        'videos_this_week': videos_this_week,
        'channels_this_week': channels_this_week,
        'users_this_month': users_this_month,
        'videos_this_month': videos_this_month,
        'channels_this_month': channels_this_month,
        'top_videos': top_videos,
        'top_channels': top_channels,
    }
    
    return render(request, 'custom_admin/dashboard.html', context)


@superuser_required
def user_management(request):
    """User management page"""
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', 'all')
    
    users = User.objects.all().order_by('-date_joined')
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Apply status filter
    if filter_type == 'active':
        users = users.filter(is_active=True)
    elif filter_type == 'inactive':
        users = users.filter(is_active=False)
    elif filter_type == 'staff':
        users = users.filter(is_staff=True)
    elif filter_type == 'creators':
        users = users.filter(is_creator=True)
    elif filter_type == 'verified':
        users = users.filter(is_verified_creator=True)
    
    # Pagination
    paginator = Paginator(users, 25)
    page = request.GET.get('page')
    
    try:
        users_page = paginator.page(page)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)
    
    context = {
        'users': users_page,
        'search_query': search_query,
        'filter_type': filter_type,
    }
    
    return render(request, 'custom_admin/user_management.html', context)


@superuser_required
def user_detail(request, user_id):
    """User detail and edit page"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_active':
            user.is_active = not user.is_active
            user.save()
            status = 'activated' if user.is_active else 'deactivated'
            messages.success(request, f'User {user.username} has been {status}.')
            
        elif action == 'toggle_staff':
            user.is_staff = not user.is_staff
            user.save()
            status = 'granted' if user.is_staff else 'removed'
            messages.success(request, f'Staff privileges {status} for user {user.username}.')
            
        elif action == 'toggle_verified':
            user.is_verified_creator = not user.is_verified_creator
            user.save()
            status = 'verified' if user.is_verified_creator else 'unverified'
            messages.success(request, f'Creator verification {status} for user {user.username}.')
        
        return redirect('custom_admin:user_detail', user_id=user.id)
    
    # Get user statistics
    try:
        channel = user.channel
        channel_videos = channel.videos.count()
        channel_subscribers = channel.subscriber_count
        total_views = channel.videos.aggregate(total=Sum('view_count'))['total'] or 0
    except:
        channel = None
        channel_videos = 0
        channel_subscribers = 0
        total_views = 0
    
    context = {
        'profile_user': user,
        'channel': channel,
        'channel_videos': channel_videos,
        'channel_subscribers': channel_subscribers,
        'total_views': total_views,
    }
    
    return render(request, 'custom_admin/user_detail.html', context)


@superuser_required
def video_management(request):
    """Video management page"""
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', 'all')
    category_filter = request.GET.get('category', '')
    
    videos = Video.objects.select_related('channel__user').order_by('-uploaded_at')
    
    # Apply search filter
    if search_query:
        videos = videos.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query) |
            Q(channel__name__icontains=search_query)
        )
    
    # Apply status filter
    if filter_type == 'public':
        videos = videos.filter(visibility='public')
    elif filter_type == 'private':
        videos = videos.filter(visibility='private')
    elif filter_type == 'unlisted':
        videos = videos.filter(visibility='unlisted')
    elif filter_type == 'processing':
        videos = videos.filter(processing_status='processing')
    elif filter_type == 'failed':
        videos = videos.filter(processing_status='failed')
    
    # Apply category filter
    if category_filter:
        videos = videos.filter(category=category_filter)
    
    # Pagination
    paginator = Paginator(videos, 20)
    page = request.GET.get('page')
    
    try:
        videos_page = paginator.page(page)
    except PageNotAnInteger:
        videos_page = paginator.page(1)
    except EmptyPage:
        videos_page = paginator.page(paginator.num_pages)
    
    # Get categories for filter dropdown
    categories = Video.CATEGORY_CHOICES
    
    context = {
        'videos': videos_page,
        'search_query': search_query,
        'filter_type': filter_type,
        'category_filter': category_filter,
        'categories': categories,
    }
    
    return render(request, 'custom_admin/video_management.html', context)


@superuser_required
def video_detail(request, video_id):
    """Video detail and edit page"""
    video = get_object_or_404(Video, id=video_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_visibility':
            new_visibility = request.POST.get('visibility')
            if new_visibility in ['public', 'private', 'unlisted']:
                video.visibility = new_visibility
                video.save()
                messages.success(request, f'Video visibility changed to {new_visibility}.')
        
        elif action == 'delete_video':
            video_title = video.title
            video.delete()
            messages.success(request, f'Video "{video_title}" has been deleted.')
            return redirect('custom_admin:video_management')
        
        return redirect('custom_admin:video_detail', video_id=video.id)
    
    context = {
        'video': video,
    }
    
    return render(request, 'custom_admin/video_detail.html', context)


@superuser_required
def channel_management(request):
    """Channel management page"""
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', 'all')
    category_filter = request.GET.get('category', '')
    
    channels = Channel.objects.select_related('user').order_by('-created_at')
    
    # Apply search filter
    if search_query:
        channels = channels.filter(
            Q(name__icontains=search_query) |
            Q(handle__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Apply status filter
    if filter_type == 'active':
        channels = channels.filter(is_active=True)
    elif filter_type == 'inactive':
        channels = channels.filter(is_active=False)
    elif filter_type == 'monetized':
        channels = channels.filter(is_monetized=True)
    elif filter_type == 'verified':
        channels = channels.filter(user__is_verified_creator=True)
    
    # Apply category filter
    if category_filter:
        channels = channels.filter(category=category_filter)
    
    # Pagination
    paginator = Paginator(channels, 20)
    page = request.GET.get('page')
    
    try:
        channels_page = paginator.page(page)
    except PageNotAnInteger:
        channels_page = paginator.page(1)
    except EmptyPage:
        channels_page = paginator.page(paginator.num_pages)
    
    # Get categories for filter dropdown
    categories = Channel.CATEGORY_CHOICES
    
    context = {
        'channels': channels_page,
        'search_query': search_query,
        'filter_type': filter_type,
        'category_filter': category_filter,
        'categories': categories,
    }
    
    return render(request, 'custom_admin/channel_management.html', context)


@superuser_required
def channel_detail(request, channel_id):
    """Channel detail and edit page"""
    channel = get_object_or_404(Channel, id=channel_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_active':
            channel.is_active = not channel.is_active
            channel.save()
            status = 'activated' if channel.is_active else 'deactivated'
            messages.success(request, f'Channel {channel.name} has been {status}.')
            
        elif action == 'toggle_monetized':
            channel.is_monetized = not channel.is_monetized
            channel.save()
            status = 'enabled' if channel.is_monetized else 'disabled'
            messages.success(request, f'Monetization {status} for channel {channel.name}.')
        
        return redirect('custom_admin:channel_detail', channel_id=channel.id)
    
    # Get channel videos
    channel_videos = channel.videos.order_by('-uploaded_at')[:10]
    
    context = {
        'channel': channel,
        'channel_videos': channel_videos,
    }
    
    return render(request, 'custom_admin/channel_detail.html', context)


@superuser_required
@require_POST
@csrf_protect
def bulk_action(request):
    """Handle bulk actions for users, videos, or channels"""
    action = request.POST.get('action')
    item_type = request.POST.get('type')
    item_ids = request.POST.getlist('items')
    
    if not action or not item_type or not item_ids:
        return JsonResponse({'success': False, 'message': 'Missing required data'})
    
    try:
        if item_type == 'users':
            users = User.objects.filter(id__in=item_ids)
            if action == 'activate':
                users.update(is_active=True)
                message = f'{users.count()} users activated'
            elif action == 'deactivate':
                users.update(is_active=False)
                message = f'{users.count()} users deactivated'
            elif action == 'make_staff':
                users.update(is_staff=True)
                message = f'{users.count()} users made staff'
            elif action == 'remove_staff':
                users.update(is_staff=False)
                message = f'Staff privileges removed from {users.count()} users'
        
        elif item_type == 'videos':
            videos = Video.objects.filter(id__in=item_ids)
            if action == 'make_public':
                videos.update(visibility='public')
                message = f'{videos.count()} videos made public'
            elif action == 'make_private':
                videos.update(visibility='private')
                message = f'{videos.count()} videos made private'
            elif action == 'delete':
                count = videos.count()
                videos.delete()
                message = f'{count} videos deleted'
        
        elif item_type == 'channels':
            channels = Channel.objects.filter(id__in=item_ids)
            if action == 'activate':
                channels.update(is_active=True)
                message = f'{channels.count()} channels activated'
            elif action == 'deactivate':
                channels.update(is_active=False)
                message = f'{channels.count()} channels deactivated'
            elif action == 'enable_monetization':
                channels.update(is_monetized=True)
                message = f'Monetization enabled for {channels.count()} channels'
            elif action == 'disable_monetization':
                channels.update(is_monetized=False)
                message = f'Monetization disabled for {channels.count()} channels'
        
        else:
            return JsonResponse({'success': False, 'message': 'Invalid item type'})
        
        return JsonResponse({'success': True, 'message': message})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
