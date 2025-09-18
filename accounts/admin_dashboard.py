"""
PlayBharat Admin Dashboard Views
Comprehensive analytics and reporting system for admin control
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.urls import path
from datetime import datetime, timedelta
import json
import csv

from django.contrib.auth import get_user_model
from .admin_models import AdminAction, UserStrike, ContentFlag, UserSuspension, ChannelSuspension
from .models import Channel
from videos.models import Video

User = get_user_model()

def superuser_required(user):
    """Check if user is superuser"""
    return user.is_authenticated and user.is_superuser

@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with comprehensive analytics"""
    
    # Time ranges for analytics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User Statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    banned_users = User.objects.filter(is_banned=True).count()
    suspended_users = User.objects.filter(is_suspended=True).count()
    warned_users = User.objects.filter(is_warned=True).count()
    
    # New registrations
    new_users_week = User.objects.filter(date_joined__date__gte=week_ago).count()
    new_users_month = User.objects.filter(date_joined__date__gte=month_ago).count()
    
    # Channel Statistics
    total_channels = Channel.objects.count()
    active_channels = Channel.objects.filter(is_active=True).count()
    verified_channels = Channel.objects.filter(is_verified=True).count()
    suspended_channels = Channel.objects.filter(is_suspended=True).count()
    
    # Video Statistics
    total_videos = Video.objects.count()
    published_videos = Video.objects.filter(is_published=True, is_active=True).count()
    flagged_videos = Video.objects.filter(is_flagged=True).count()
    videos_under_review = Video.objects.filter(requires_review=True).count()
    
    # Content Moderation Statistics
    total_strikes = UserStrike.objects.count()
    active_strikes = UserStrike.objects.filter(is_active=True).count()
    pending_flags = ContentFlag.objects.filter(status='pending').count()
    resolved_flags = ContentFlag.objects.filter(status='resolved').count()
    
    # Recent Admin Actions (last 10)
    recent_actions = AdminAction.objects.select_related('admin_user', 'target_user')[:10]
    
    # Strike Distribution
    strike_distribution = UserStrike.objects.values('strike_type').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Flag Distribution
    flag_distribution = ContentFlag.objects.values('flag_type').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Weekly User Registration Chart Data
    weekly_registrations = User.objects.filter(
        date_joined__date__gte=month_ago
    ).extra({'date': 'date(date_joined)'}).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Monthly Strike Chart Data
    monthly_strikes = UserStrike.objects.filter(
        created_at__date__gte=today - timedelta(days=90)
    ).extra({'month': 'date_trunc(\'month\', created_at)'}).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Top Flagged Content
    top_flagged_videos = Video.objects.filter(
        contentflag__isnull=False
    ).annotate(
        flag_count=Count('contentflag')
    ).order_by('-flag_count')[:5]
    
    context = {
        # User stats
        'total_users': total_users,
        'active_users': active_users,
        'banned_users': banned_users,
        'suspended_users': suspended_users,
        'warned_users': warned_users,
        'new_users_week': new_users_week,
        'new_users_month': new_users_month,
        
        # Channel stats
        'total_channels': total_channels,
        'active_channels': active_channels,
        'verified_channels': verified_channels,
        'suspended_channels': suspended_channels,
        
        # Video stats
        'total_videos': total_videos,
        'published_videos': published_videos,
        'flagged_videos': flagged_videos,
        'videos_under_review': videos_under_review,
        
        # Moderation stats
        'total_strikes': total_strikes,
        'active_strikes': active_strikes,
        'pending_flags': pending_flags,
        'resolved_flags': resolved_flags,
        
        # Recent data
        'recent_actions': recent_actions,
        'strike_distribution': strike_distribution,
        'flag_distribution': flag_distribution,
        'top_flagged_videos': top_flagged_videos,
        
        # Chart data
        'weekly_registrations': json.dumps(list(weekly_registrations)),
        'monthly_strikes': json.dumps(list(monthly_strikes)),
    }
    
    return render(request, 'admin/dashboard.html', context)


@user_passes_test(superuser_required)
def user_management(request):
    """Comprehensive user management interface"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-date_joined')
    
    # Build queryset
    users = User.objects.all()
    
    if status_filter == 'banned':
        users = users.filter(is_banned=True)
    elif status_filter == 'suspended':
        users = users.filter(is_suspended=True)
    elif status_filter == 'warned':
        users = users.filter(is_warned=True)
    elif status_filter == 'active':
        users = users.filter(is_active=True, is_banned=False, is_suspended=False)
    elif status_filter == 'staff':
        users = users.filter(is_staff=True)
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Sort users
    valid_sort_fields = [
        'username', '-username', 'email', '-email', 'date_joined', 
        '-date_joined', 'last_login', '-last_login', 'strike_count', 
        '-strike_count'
    ]
    if sort_by in valid_sort_fields:
        users = users.order_by(sort_by)
    
    # Add annotations
    users = users.annotate(
        total_strikes=Count('strikes'),
        total_videos=Count('channels__videos'),
        total_channels=Count('channels')
    )
    
    # Pagination
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_count = users.count()
    banned_count = users.filter(is_banned=True).count()
    suspended_count = users.filter(is_suspended=True).count()
    
    context = {
        'page_obj': page_obj,
        'total_count': total_count,
        'banned_count': banned_count,
        'suspended_count': suspended_count,
        'status_filter': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    return render(request, 'admin/user_management.html', context)


@user_passes_test(superuser_required)
def content_moderation(request):
    """Content moderation dashboard"""
    
    # Get filter parameters
    content_type = request.GET.get('type', 'videos')
    status_filter = request.GET.get('status', 'all')
    flag_type = request.GET.get('flag_type', 'all')
    
    if content_type == 'flags':
        # Content flags
        flags = ContentFlag.objects.select_related(
            'reported_by', 'reviewed_by', 'flagged_video', 'flagged_user', 'flagged_channel'
        )
        
        if status_filter != 'all':
            flags = flags.filter(status=status_filter)
        
        if flag_type != 'all':
            flags = flags.filter(flag_type=flag_type)
        
        # Pagination
        paginator = Paginator(flags.order_by('-created_at'), 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Statistics
        pending_count = ContentFlag.objects.filter(status='pending').count()
        reviewing_count = ContentFlag.objects.filter(status='reviewing').count()
        resolved_count = ContentFlag.objects.filter(status='resolved').count()
        
        context = {
            'content_type': content_type,
            'page_obj': page_obj,
            'status_filter': status_filter,
            'flag_type': flag_type,
            'pending_count': pending_count,
            'reviewing_count': reviewing_count,
            'resolved_count': resolved_count,
            'flag_types': ContentFlag.FLAG_TYPES,
            'status_choices': ContentFlag.STATUS_CHOICES,
        }
        
    elif content_type == 'strikes':
        # User strikes
        strikes = UserStrike.objects.select_related(
            'user', 'issued_by', 'resolved_by', 'related_video', 'related_channel'
        )
        
        if status_filter == 'active':
            strikes = strikes.filter(is_active=True)
        elif status_filter == 'expired':
            strikes = strikes.filter(is_active=False)
        
        # Pagination
        paginator = Paginator(strikes.order_by('-created_at'), 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Statistics
        active_strikes = UserStrike.objects.filter(is_active=True).count()
        total_strikes = UserStrike.objects.count()
        users_with_strikes = User.objects.filter(strikes__is_active=True).distinct().count()
        
        context = {
            'content_type': content_type,
            'page_obj': page_obj,
            'status_filter': status_filter,
            'active_strikes': active_strikes,
            'total_strikes': total_strikes,
            'users_with_strikes': users_with_strikes,
            'strike_types': UserStrike.STRIKE_TYPES,
            'severity_levels': UserStrike.SEVERITY_LEVELS,
        }
        
    else:  # videos
        # Videos requiring moderation
        videos = Video.objects.select_related('channel__owner')
        
        if status_filter == 'flagged':
            videos = videos.filter(is_flagged=True)
        elif status_filter == 'under_review':
            videos = videos.filter(requires_review=True)
        elif status_filter == 'hidden':
            videos = videos.filter(is_active=False)
        elif status_filter == 'published':
            videos = videos.filter(is_published=True, is_active=True)
        
        # Pagination
        paginator = Paginator(videos.order_by('-upload_date'), 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Statistics
        flagged_count = Video.objects.filter(is_flagged=True).count()
        review_count = Video.objects.filter(requires_review=True).count()
        hidden_count = Video.objects.filter(is_active=False).count()
        
        context = {
            'content_type': content_type,
            'page_obj': page_obj,
            'status_filter': status_filter,
            'flagged_count': flagged_count,
            'review_count': review_count,
            'hidden_count': hidden_count,
        }
    
    return render(request, 'admin/content_moderation.html', context)


@user_passes_test(superuser_required)
def analytics_report(request):
    """Detailed analytics and reporting"""
    
    # Time range selection
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # User Analytics
    user_registrations = User.objects.filter(
        date_joined__date__range=[start_date, end_date]
    ).extra({'date': 'date(date_joined)'}).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Channel Analytics
    channel_creations = Channel.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).extra({'date': 'date(created_at)'}).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Video Analytics
    video_uploads = Video.objects.filter(
        upload_date__date__range=[start_date, end_date]
    ).extra({'date': 'date(upload_date)'}).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Strike Analytics
    strike_trends = UserStrike.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).extra({'date': 'date(created_at)'}).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Top violations
    top_violations = UserStrike.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).values('strike_type').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Top flagged content types
    top_flag_types = ContentFlag.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).values('flag_type').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # User activity by location (if you have IP geolocation)
    admin_activity = AdminAction.objects.filter(
        timestamp__date__range=[start_date, end_date]
    ).values('admin_user__username').annotate(
        action_count=Count('id')
    ).order_by('-action_count')[:10]
    
    context = {
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'user_registrations': json.dumps(list(user_registrations)),
        'channel_creations': json.dumps(list(channel_creations)),
        'video_uploads': json.dumps(list(video_uploads)),
        'strike_trends': json.dumps(list(strike_trends)),
        'top_violations': top_violations,
        'top_flag_types': top_flag_types,
        'admin_activity': admin_activity,
    }
    
    return render(request, 'admin/analytics.html', context)


@user_passes_test(superuser_required)
def bulk_actions(request):
    """Bulk action interface for mass operations"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        target_type = request.POST.get('target_type')  # users, channels, videos
        target_ids = request.POST.getlist('target_ids')
        reason = request.POST.get('reason', 'Bulk admin action')
        
        if action == 'ban_users' and target_type == 'users':
            users = User.objects.filter(id__in=target_ids)
            count = 0
            
            for user in users:
                if not user.is_banned:
                    user.is_banned = True
                    user.is_active = False
                    user.ban_reason = reason
                    user.banned_at = timezone.now()
                    user.banned_by = request.user
                    user.save()
                    
                    AdminAction.objects.create(
                        admin_user=request.user,
                        action_type='user_ban',
                        target_user=user,
                        reason=reason
                    )
                    count += 1
            
            messages.success(request, f'{count} users have been banned.')
            
        elif action == 'suspend_channels' and target_type == 'channels':
            channels = Channel.objects.filter(id__in=target_ids)
            count = 0
            
            for channel in channels:
                if not channel.is_suspended:
                    channel.is_suspended = True
                    channel.suspension_reason = reason
                    channel.suspended_by = request.user
                    channel.suspended_at = timezone.now()
                    channel.save()
                    
                    ChannelSuspension.objects.create(
                        channel=channel,
                        suspended_by=request.user,
                        suspension_type='temporary',
                        reason=reason
                    )
                    
                    AdminAction.objects.create(
                        admin_user=request.user,
                        action_type='channel_suspend',
                        target_channel=channel,
                        reason=reason
                    )
                    count += 1
            
            messages.success(request, f'{count} channels have been suspended.')
            
        elif action == 'hide_videos' and target_type == 'videos':
            videos = Video.objects.filter(id__in=target_ids)
            count = 0
            
            for video in videos:
                if video.is_active:
                    video.is_active = False
                    video.save()
                    
                    AdminAction.objects.create(
                        admin_user=request.user,
                        action_type='video_hide',
                        target_video=video,
                        reason=reason
                    )
                    count += 1
            
            messages.success(request, f'{count} videos have been hidden.')
        
        return redirect('admin:bulk_actions')
    
    return render(request, 'admin/bulk_actions.html')


@user_passes_test(superuser_required)
def export_data(request):
    """Export admin data to CSV"""
    
    export_type = request.GET.get('type', 'users')
    
    response = HttpResponse(content_type='text/csv')
    
    if export_type == 'users':
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        writer = csv.writer(response)
        writer.writerow(['Username', 'Email', 'Status', 'Date Joined', 'Last Login', 'Strike Count', 'Is Banned', 'Is Suspended'])
        
        users = User.objects.annotate(
            total_strikes=Count('strikes')
        ).values_list(
            'username', 'email', 'is_active', 'date_joined', 'last_login', 
            'total_strikes', 'is_banned', 'is_suspended'
        )
        
        for user in users:
            writer.writerow(user)
            
    elif export_type == 'strikes':
        response['Content-Disposition'] = 'attachment; filename="strikes.csv"'
        writer = csv.writer(response)
        writer.writerow(['User', 'Strike Type', 'Severity', 'Reason', 'Issued By', 'Created At', 'Is Active'])
        
        strikes = UserStrike.objects.select_related('user', 'issued_by').values_list(
            'user__username', 'strike_type', 'severity', 'reason', 
            'issued_by__username', 'created_at', 'is_active'
        )
        
        for strike in strikes:
            writer.writerow(strike)
            
    elif export_type == 'flags':
        response['Content-Disposition'] = 'attachment; filename="content_flags.csv"'
        writer = csv.writer(response)
        writer.writerow(['Reported By', 'Flag Type', 'Content Type', 'Status', 'Created At', 'Reviewed By'])
        
        flags = ContentFlag.objects.select_related('reported_by', 'reviewed_by').all()
        
        for flag in flags:
            content_type = 'Video' if flag.flagged_video else ('User' if flag.flagged_user else 'Channel')
            writer.writerow([
                flag.reported_by.username,
                flag.flag_type,
                content_type,
                flag.status,
                flag.created_at,
                flag.reviewed_by.username if flag.reviewed_by else ''
            ])
    
    return response


# URL patterns for admin dashboard
urlpatterns = [
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('users/', user_management, name='user_management'),
    path('moderation/', content_moderation, name='content_moderation'),
    path('analytics/', analytics_report, name='analytics_report'),
    path('bulk-actions/', bulk_actions, name='bulk_actions'),
    path('export/', export_data, name='export_data'),
]