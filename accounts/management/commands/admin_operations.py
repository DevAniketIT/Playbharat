"""
Django Management Commands for PlayBharat Admin Operations
Comprehensive command-line tools for YouTube-like admin control
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import sys

from accounts.models import Channel
from accounts.admin_models import AdminAction, UserStrike, ContentFlag, UserSuspension, ChannelSuspension
from videos.models import Video

User = get_user_model()


class Command(BaseCommand):
    help = 'PlayBharat Admin Operations - Comprehensive user and content management'
    
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='command', help='Admin commands')
        
        # User management commands
        user_parser = subparsers.add_parser('user', help='User management operations')
        user_subparsers = user_parser.add_subparsers(dest='user_action', help='User actions')
        
        # Ban user
        ban_parser = user_subparsers.add_parser('ban', help='Ban a user')
        ban_parser.add_argument('username', help='Username to ban')
        ban_parser.add_argument('--reason', default='Admin action', help='Ban reason')
        ban_parser.add_argument('--admin', required=True, help='Admin username performing the action')
        
        # Unban user
        unban_parser = user_subparsers.add_parser('unban', help='Unban a user')
        unban_parser.add_argument('username', help='Username to unban')
        unban_parser.add_argument('--admin', required=True, help='Admin username performing the action')
        
        # Suspend user
        suspend_parser = user_subparsers.add_parser('suspend', help='Suspend a user')
        suspend_parser.add_argument('username', help='Username to suspend')
        suspend_parser.add_argument('--days', type=int, default=7, help='Suspension duration in days')
        suspend_parser.add_argument('--reason', default='Admin action', help='Suspension reason')
        suspend_parser.add_argument('--admin', required=True, help='Admin username performing the action')
        
        # Issue strike
        strike_parser = user_subparsers.add_parser('strike', help='Issue a strike to user')
        strike_parser.add_argument('username', help='Username to strike')
        strike_parser.add_argument('--type', choices=[
            'content_violation', 'spam', 'harassment', 'copyright', 'adult_content',
            'hate_speech', 'violence', 'misinformation', 'community_guidelines', 'other'
        ], required=True, help='Strike type')
        strike_parser.add_argument('--severity', choices=['warning', 'strike_1', 'strike_2', 'strike_3'], 
                                 default='strike_1', help='Strike severity')
        strike_parser.add_argument('--reason', required=True, help='Strike reason')
        strike_parser.add_argument('--admin', required=True, help='Admin username performing the action')
        
        # List users
        list_users_parser = user_subparsers.add_parser('list', help='List users with filters')
        list_users_parser.add_argument('--banned', action='store_true', help='Show only banned users')
        list_users_parser.add_argument('--suspended', action='store_true', help='Show only suspended users')
        list_users_parser.add_argument('--strikes', action='store_true', help='Show users with active strikes')
        list_users_parser.add_argument('--limit', type=int, default=50, help='Maximum number of results')
        
        # Channel management commands
        channel_parser = subparsers.add_parser('channel', help='Channel management operations')
        channel_subparsers = channel_parser.add_subparsers(dest='channel_action', help='Channel actions')
        
        # Suspend channel
        channel_suspend_parser = channel_subparsers.add_parser('suspend', help='Suspend a channel')
        channel_suspend_parser.add_argument('channel_name', help='Channel name to suspend')
        channel_suspend_parser.add_argument('--reason', default='Admin action', help='Suspension reason')
        channel_suspend_parser.add_argument('--admin', required=True, help='Admin username performing the action')
        
        # Video management commands
        video_parser = subparsers.add_parser('video', help='Video management operations')
        video_subparsers = video_parser.add_subparsers(dest='video_action', help='Video actions')
        
        # Hide video
        hide_video_parser = video_subparsers.add_parser('hide', help='Hide a video')
        hide_video_parser.add_argument('video_id', type=int, help='Video ID to hide')
        hide_video_parser.add_argument('--reason', default='Admin action', help='Reason for hiding')
        hide_video_parser.add_argument('--admin', required=True, help='Admin username performing the action')
        
        # Statistics commands
        stats_parser = subparsers.add_parser('stats', help='Platform statistics')
        stats_parser.add_argument('--detailed', action='store_true', help='Show detailed statistics')
        
        # Cleanup commands
        cleanup_parser = subparsers.add_parser('cleanup', help='Database cleanup operations')
        cleanup_parser.add_argument('--expired-strikes', action='store_true', help='Remove expired strikes')
        cleanup_parser.add_argument('--old-actions', action='store_true', help='Archive old admin actions')
        cleanup_parser.add_argument('--days', type=int, default=90, help='Days threshold for cleanup')
        
        # Export commands
        export_parser = subparsers.add_parser('export', help='Export data operations')
        export_parser.add_argument('--type', choices=['users', 'strikes', 'flags', 'actions'], 
                                 required=True, help='Data type to export')
        export_parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='Export format')
        export_parser.add_argument('--output', help='Output file path')
    
    def handle(self, *args, **options):
        command = options['command']
        
        if command == 'user':
            self.handle_user_command(options)
        elif command == 'channel':
            self.handle_channel_command(options)
        elif command == 'video':
            self.handle_video_command(options)
        elif command == 'stats':
            self.handle_stats_command(options)
        elif command == 'cleanup':
            self.handle_cleanup_command(options)
        elif command == 'export':
            self.handle_export_command(options)
        else:
            self.stdout.write(self.style.ERROR('Unknown command. Use --help for available commands.'))
    
    def handle_user_command(self, options):
        action = options['user_action']
        
        if action == 'ban':
            self.ban_user(options)
        elif action == 'unban':
            self.unban_user(options)
        elif action == 'suspend':
            self.suspend_user(options)
        elif action == 'strike':
            self.issue_strike(options)
        elif action == 'list':
            self.list_users(options)
    
    def ban_user(self, options):
        """Ban a user"""
        username = options['username']
        reason = options['reason']
        admin_username = options['admin']
        
        try:
            user = User.objects.get(username=username)
            admin_user = User.objects.get(username=admin_username)
            
            if not admin_user.is_staff:
                raise CommandError(f'{admin_username} is not a staff member')
            
            if user.is_banned:
                self.stdout.write(self.style.WARNING(f'User {username} is already banned'))
                return
            
            with transaction.atomic():
                # Ban user
                user.is_banned = True
                user.is_active = False
                user.ban_reason = reason
                user.banned_at = timezone.now()
                user.banned_by = admin_user
                user.save()
                
                # Suspend all user's channels
                for channel in user.channels.all():
                    channel.is_suspended = True
                    channel.suspension_reason = f"User banned: {reason}"
                    channel.suspended_by = admin_user
                    channel.suspended_at = timezone.now()
                    channel.save()
                
                # Log admin action
                AdminAction.objects.create(
                    admin_user=admin_user,
                    action_type='user_ban',
                    target_user=user,
                    reason=reason
                )
                
            self.stdout.write(self.style.SUCCESS(f'User {username} has been banned successfully'))
            
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist')
    
    def unban_user(self, options):
        """Unban a user"""
        username = options['username']
        admin_username = options['admin']
        
        try:
            user = User.objects.get(username=username)
            admin_user = User.objects.get(username=admin_username)
            
            if not admin_user.is_staff:
                raise CommandError(f'{admin_username} is not a staff member')
            
            if not user.is_banned:
                self.stdout.write(self.style.WARNING(f'User {username} is not banned'))
                return
            
            with transaction.atomic():
                # Unban user
                user.is_banned = False
                user.is_active = True
                user.ban_reason = ""
                user.banned_at = None
                user.banned_by = None
                user.save()
                
                # Restore user's channels
                for channel in user.channels.all():
                    channel.is_suspended = False
                    channel.suspension_reason = ""
                    channel.suspended_by = None
                    channel.suspended_at = None
                    channel.save()
                
                # Log admin action
                AdminAction.objects.create(
                    admin_user=admin_user,
                    action_type='user_unban',
                    target_user=user,
                    reason="User unbanned"
                )
                
            self.stdout.write(self.style.SUCCESS(f'User {username} has been unbanned successfully'))
            
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist')
    
    def issue_strike(self, options):
        """Issue a strike to user"""
        username = options['username']
        strike_type = options['type']
        severity = options['severity']
        reason = options['reason']
        admin_username = options['admin']
        
        try:
            user = User.objects.get(username=username)
            admin_user = User.objects.get(username=admin_username)
            
            if not admin_user.is_staff:
                raise CommandError(f'{admin_username} is not a staff member')
            
            # Create strike
            strike = UserStrike.objects.create(
                user=user,
                issued_by=admin_user,
                strike_type=strike_type,
                severity=severity,
                reason=reason
            )
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=admin_user,
                action_type='user_strike',
                target_user=user,
                reason=f"Strike issued: {reason}"
            )
            
            self.stdout.write(self.style.SUCCESS(
                f'Strike issued to {username}: {strike.get_strike_type_display()} '
                f'({strike.get_severity_display()})'
            ))
            
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist')
    
    def list_users(self, options):
        """List users with filters"""
        users = User.objects.all()
        
        if options['banned']:
            users = users.filter(is_banned=True)
        if options['suspended']:
            users = users.filter(is_suspended=True)
        if options['strikes']:
            users = users.filter(strikes__is_active=True).distinct()
        
        users = users[:options['limit']]
        
        self.stdout.write("Username\t\tEmail\t\t\tStatus\t\tStrikes\tJoined")
        self.stdout.write("-" * 80)
        
        for user in users:
            status_parts = []
            if user.is_banned:
                status_parts.append("BANNED")
            elif user.is_suspended:
                status_parts.append("SUSPENDED")
            elif user.is_warned:
                status_parts.append("WARNED")
            else:
                status_parts.append("ACTIVE")
            
            status = "/".join(status_parts)
            strike_count = user.strikes.filter(is_active=True).count()
            
            self.stdout.write(
                f"{user.username[:15]:<15}\t{user.email[:25]:<25}\t{status:<10}\t"
                f"{strike_count}\t{user.date_joined.strftime('%Y-%m-%d')}"
            )
    
    def handle_stats_command(self, options):
        """Show platform statistics"""
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        banned_users = User.objects.filter(is_banned=True).count()
        suspended_users = User.objects.filter(is_suspended=True).count()
        
        # Content statistics
        total_channels = Channel.objects.count()
        active_channels = Channel.objects.filter(is_active=True).count()
        total_videos = Video.objects.count()
        published_videos = Video.objects.filter(is_published=True, is_active=True).count()
        
        # Moderation statistics
        total_strikes = UserStrike.objects.count()
        active_strikes = UserStrike.objects.filter(is_active=True).count()
        pending_flags = ContentFlag.objects.filter(status='pending').count()
        
        self.stdout.write(self.style.SUCCESS("=== PlayBharat Platform Statistics ==="))
        self.stdout.write(f"Users:")
        self.stdout.write(f"  Total: {total_users}")
        self.stdout.write(f"  Active: {active_users}")
        self.stdout.write(f"  Banned: {banned_users}")
        self.stdout.write(f"  Suspended: {suspended_users}")
        
        self.stdout.write(f"\nContent:")
        self.stdout.write(f"  Channels: {total_channels} (Active: {active_channels})")
        self.stdout.write(f"  Videos: {total_videos} (Published: {published_videos})")
        
        self.stdout.write(f"\nModeration:")
        self.stdout.write(f"  Total Strikes: {total_strikes} (Active: {active_strikes})")
        self.stdout.write(f"  Pending Flags: {pending_flags}")
        
        if options['detailed']:
            # Detailed statistics
            recent_registrations = User.objects.filter(
                date_joined__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            strike_distribution = UserStrike.objects.values('strike_type').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            self.stdout.write(f"\nDetailed Statistics:")
            self.stdout.write(f"  New registrations (7 days): {recent_registrations}")
            self.stdout.write(f"  Top strike types:")
            for strike in strike_distribution:
                self.stdout.write(f"    {strike['strike_type']}: {strike['count']}")
    
    def handle_cleanup_command(self, options):
        """Handle database cleanup operations"""
        days_threshold = options['days']
        cutoff_date = timezone.now() - timedelta(days=days_threshold)
        
        if options['expired_strikes']:
            # Remove expired strikes
            expired_strikes = UserStrike.objects.filter(
                expires_at__lt=timezone.now(),
                is_active=True
            )
            count = expired_strikes.count()
            expired_strikes.update(is_active=False, resolved_at=timezone.now())
            
            self.stdout.write(self.style.SUCCESS(f'Cleaned up {count} expired strikes'))
        
        if options['old_actions']:
            # Archive old admin actions
            old_actions = AdminAction.objects.filter(timestamp__lt=cutoff_date)
            count = old_actions.count()
            
            # In a real implementation, you might move these to an archive table
            # For now, we'll just report the count
            self.stdout.write(self.style.SUCCESS(
                f'Found {count} admin actions older than {days_threshold} days that can be archived'
            ))
    
    def handle_export_command(self, options):
        """Handle data export operations"""
        export_type = options['type']
        format_type = options['format']
        output_file = options.get('output') or f'{export_type}_export.{format_type}'
        
        if export_type == 'users':
            self.export_users(output_file, format_type)
        elif export_type == 'strikes':
            self.export_strikes(output_file, format_type)
        # Add more export types as needed
        
        self.stdout.write(self.style.SUCCESS(f'Data exported to {output_file}'))
    
    def export_users(self, filename, format_type):
        """Export users data"""
        users = User.objects.annotate(
            total_strikes=Count('strikes')
        ).values(
            'username', 'email', 'is_active', 'is_banned', 'is_suspended',
            'date_joined', 'last_login', 'total_strikes'
        )
        
        if format_type == 'csv':
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['username', 'email', 'is_active', 'is_banned', 'is_suspended', 
                             'date_joined', 'last_login', 'total_strikes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for user in users:
                    writer.writerow(user)
        
        elif format_type == 'json':
            import json
            from django.core.serializers.json import DjangoJSONEncoder
            
            users_list = list(users)
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(users_list, jsonfile, cls=DjangoJSONEncoder, indent=2)
    
    def handle_channel_command(self, options):
        """Handle channel management commands"""
        action = options['channel_action']
        
        if action == 'suspend':
            self.suspend_channel(options)
    
    def suspend_channel(self, options):
        """Suspend a channel"""
        channel_name = options['channel_name']
        reason = options['reason']
        admin_username = options['admin']
        
        try:
            channel = Channel.objects.get(name=channel_name)
            admin_user = User.objects.get(username=admin_username)
            
            if not admin_user.is_staff:
                raise CommandError(f'{admin_username} is not a staff member')
            
            with transaction.atomic():
                channel.is_suspended = True
                channel.suspension_reason = reason
                channel.suspended_by = admin_user
                channel.suspended_at = timezone.now()
                channel.save()
                
                # Create suspension record
                ChannelSuspension.objects.create(
                    channel=channel,
                    suspended_by=admin_user,
                    suspension_type='temporary',
                    reason=reason
                )
                
                # Log admin action
                AdminAction.objects.create(
                    admin_user=admin_user,
                    action_type='channel_suspend',
                    target_channel=channel,
                    reason=reason
                )
            
            self.stdout.write(self.style.SUCCESS(f'Channel "{channel_name}" has been suspended'))
            
        except Channel.DoesNotExist:
            raise CommandError(f'Channel "{channel_name}" does not exist')
        except User.DoesNotExist:
            raise CommandError(f'Admin user "{admin_username}" does not exist')
    
    def handle_video_command(self, options):
        """Handle video management commands"""
        action = options['video_action']
        
        if action == 'hide':
            self.hide_video(options)
    
    def hide_video(self, options):
        """Hide a video"""
        video_id = options['video_id']
        reason = options['reason']
        admin_username = options['admin']
        
        try:
            video = Video.objects.get(id=video_id)
            admin_user = User.objects.get(username=admin_username)
            
            if not admin_user.is_staff:
                raise CommandError(f'{admin_username} is not a staff member')
            
            video.is_active = False
            video.save()
            
            # Log admin action
            AdminAction.objects.create(
                admin_user=admin_user,
                action_type='video_hide',
                target_video=video,
                reason=reason
            )
            
            self.stdout.write(self.style.SUCCESS(f'Video {video_id} "{video.title}" has been hidden'))
            
        except Video.DoesNotExist:
            raise CommandError(f'Video with ID {video_id} does not exist')
        except User.DoesNotExist:
            raise CommandError(f'Admin user "{admin_username}" does not exist')