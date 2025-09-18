"""
Professional content moderation management command for PlayBharat
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from interactions.models import Report, Comment
from videos.models import Video
from accounts.models import Channel
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Professional content moderation tools for PlayBharat platform'

    def add_arguments(self, parser):
        parser.add_argument('--action', type=str, choices=['reports', 'stats', 'cleanup'], 
                           help='Action to perform')
        parser.add_argument('--auto-resolve', action='store_true', 
                           help='Auto resolve spam reports')

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 PlayBharat Content Moderation Tools')
        )
        self.stdout.write('=' * 50)

        action = options.get('action')
        
        if action == 'reports':
            self.show_reports()
        elif action == 'stats':
            self.show_moderation_stats()
        elif action == 'cleanup':
            self.cleanup_content(options.get('auto_resolve', False))
        else:
            self.show_menu()

    def show_menu(self):
        """Show moderation menu"""
        self.stdout.write('Available moderation actions:')
        self.stdout.write('1. View pending reports: --action reports')
        self.stdout.write('2. Show moderation stats: --action stats')
        self.stdout.write('3. Cleanup content: --action cleanup')

    def show_reports(self):
        """Show pending reports"""
        pending_reports = Report.objects.filter(status='pending')
        
        self.stdout.write(f'\n📋 PENDING REPORTS ({pending_reports.count()}):')
        self.stdout.write('-' * 40)
        
        for report in pending_reports[:10]:  # Show first 10
            self.stdout.write(f'ID: {report.id}')
            self.stdout.write(f'Type: {report.content_type}')
            self.stdout.write(f'Reason: {report.reason}')
            self.stdout.write(f'Reporter: {report.reporter.username}')
            self.stdout.write(f'Date: {report.created_at}')
            if report.description:
                self.stdout.write(f'Description: {report.description[:100]}...')
            self.stdout.write('-' * 40)

    def show_moderation_stats(self):
        """Show moderation statistics"""
        total_reports = Report.objects.count()
        pending_reports = Report.objects.filter(status='pending').count()
        resolved_reports = Report.objects.filter(status='resolved').count()
        
        total_comments = Comment.objects.count()
        hidden_comments = Comment.objects.filter(is_hidden=True).count()
        
        total_videos = Video.objects.count()
        private_videos = Video.objects.filter(visibility='private').count()
        
        self.stdout.write('\n📊 MODERATION STATISTICS:')
        self.stdout.write('=' * 30)
        self.stdout.write(f'Total Reports: {total_reports}')
        self.stdout.write(f'Pending Reports: {pending_reports}')
        self.stdout.write(f'Resolved Reports: {resolved_reports}')
        self.stdout.write('')
        self.stdout.write(f'Total Comments: {total_comments}')
        self.stdout.write(f'Hidden Comments: {hidden_comments}')
        self.stdout.write('')
        self.stdout.write(f'Total Videos: {total_videos}')
        self.stdout.write(f'Private Videos: {private_videos}')

    def cleanup_content(self, auto_resolve=False):
        """Cleanup and moderate content"""
        self.stdout.write('\n🧹 CONTENT CLEANUP:')
        self.stdout.write('=' * 25)
        
        # Hide comments with excessive reports
        problematic_comments = Comment.objects.filter(
            is_hidden=False
        ).annotate(
            report_count=models.Count('report')
        ).filter(report_count__gte=3)
        
        hidden_count = 0
        for comment in problematic_comments:
            comment.is_hidden = True
            comment.save()
            hidden_count += 1
        
        self.stdout.write(f'Hidden {hidden_count} problematic comments')
        
        if auto_resolve:
            # Auto-resolve obvious spam reports
            spam_reports = Report.objects.filter(
                status='pending',
                reason='spam'
            )
            
            resolved_count = 0
            for report in spam_reports:
                report.status = 'resolved'
                report.moderator_notes = 'Auto-resolved by system'
                report.save()
                resolved_count += 1
            
            self.stdout.write(f'Auto-resolved {resolved_count} spam reports')
        
        self.stdout.write('✅ Content cleanup completed!')