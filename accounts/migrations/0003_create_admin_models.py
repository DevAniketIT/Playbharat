# Generated manually for PlayBharat admin moderation system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_add_admin_control_fields'),
        ('videos', '0001_initial'),  # Assuming videos app exists
    ]

    operations = [
        # Create AdminAction table
        migrations.CreateModel(
            name='AdminAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[
                    ('user_ban', 'User Banned'), ('user_unban', 'User Unbanned'), 
                    ('user_delete', 'User Deleted'), ('user_restore', 'User Restored'), 
                    ('user_strike', 'User Strike Issued'), ('user_warning', 'User Warning Issued'), 
                    ('channel_delete', 'Channel Deleted'), ('channel_suspend', 'Channel Suspended'), 
                    ('channel_restore', 'Channel Restored'), ('video_delete', 'Video Deleted'), 
                    ('video_hide', 'Video Hidden'), ('video_restore', 'Video Restored'), 
                    ('password_reset', 'Password Reset'), ('role_change', 'Role Changed'), 
                    ('verification_grant', 'Verification Granted'), ('verification_revoke', 'Verification Revoked'), 
                    ('monetization_enable', 'Monetization Enabled'), ('monetization_disable', 'Monetization Disabled')
                ], max_length=30)),
                ('reason', models.TextField()),
                ('details', models.JSONField(blank=True, default=dict)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('admin_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                               related_name='admin_actions', to=settings.AUTH_USER_MODEL)),
                ('target_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                                 related_name='received_actions', to=settings.AUTH_USER_MODEL)),
                ('target_channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                                   to='accounts.channel')),
                ('target_video', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                                 to='videos.video')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),

        # Create UserStrike table
        migrations.CreateModel(
            name='UserStrike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strike_type', models.CharField(choices=[
                    ('content_violation', 'Content Policy Violation'), ('spam', 'Spam or Misleading Content'), 
                    ('harassment', 'Harassment or Bullying'), ('copyright', 'Copyright Infringement'), 
                    ('adult_content', 'Adult Content'), ('hate_speech', 'Hate Speech'), 
                    ('violence', 'Violence or Dangerous Content'), ('misinformation', 'Misinformation'), 
                    ('community_guidelines', 'Community Guidelines Violation'), ('other', 'Other Violation')
                ], max_length=30)),
                ('severity', models.CharField(choices=[
                    ('warning', 'Warning'), ('strike_1', 'First Strike'), 
                    ('strike_2', 'Second Strike'), ('strike_3', 'Third Strike (Final)')
                ], max_length=15)),
                ('reason', models.TextField()),
                ('details', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                         related_name='strikes', to=settings.AUTH_USER_MODEL)),
                ('issued_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                              related_name='issued_strikes', to=settings.AUTH_USER_MODEL)),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                                 related_name='resolved_strikes', to=settings.AUTH_USER_MODEL)),
                ('related_video', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                                  to='videos.video')),
                ('related_channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                                    to='accounts.channel')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Create ContentFlag table
        migrations.CreateModel(
            name='ContentFlag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flag_type', models.CharField(choices=[
                    ('inappropriate', 'Inappropriate Content'), ('spam', 'Spam'), 
                    ('harassment', 'Harassment'), ('hate_speech', 'Hate Speech'), 
                    ('violence', 'Violence'), ('adult_content', 'Adult Content'), 
                    ('copyright', 'Copyright Violation'), ('misinformation', 'Misinformation'), 
                    ('dangerous', 'Dangerous Content'), ('other', 'Other')
                ], max_length=20)),
                ('description', models.TextField()),
                ('additional_info', models.TextField(blank=True)),
                ('status', models.CharField(choices=[
                    ('pending', 'Pending Review'), ('reviewing', 'Under Review'), 
                    ('resolved', 'Resolved'), ('dismissed', 'Dismissed'), ('escalated', 'Escalated')
                ], default='pending', max_length=15)),
                ('review_notes', models.TextField(blank=True)),
                ('action_taken', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('reported_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                                related_name='submitted_flags', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                                related_name='reviewed_flags', to=settings.AUTH_USER_MODEL)),
                ('flagged_video', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, 
                                                  to='videos.video')),
                ('flagged_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, 
                                                 related_name='received_flags', to=settings.AUTH_USER_MODEL)),
                ('flagged_channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, 
                                                    to='accounts.channel')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Create UserSuspension table
        migrations.CreateModel(
            name='UserSuspension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suspension_type', models.CharField(choices=[
                    ('temporary', 'Temporary Suspension'), ('permanent', 'Permanent Ban'), 
                    ('shadow_ban', 'Shadow Ban'), ('upload_ban', 'Upload Ban'), ('comment_ban', 'Comment Ban')
                ], max_length=20)),
                ('reason', models.TextField()),
                ('details', models.TextField(blank=True)),
                ('starts_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('lifted_at', models.DateTimeField(blank=True, null=True)),
                ('lift_reason', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                         related_name='suspensions', to=settings.AUTH_USER_MODEL)),
                ('suspended_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                                 related_name='issued_suspensions', to=settings.AUTH_USER_MODEL)),
                ('lifted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                              related_name='lifted_suspensions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Create ChannelSuspension table
        migrations.CreateModel(
            name='ChannelSuspension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suspension_type', models.CharField(choices=[
                    ('temporary', 'Temporary Suspension'), ('permanent', 'Permanent Suspension'), 
                    ('monetization_disabled', 'Monetization Disabled'), ('upload_disabled', 'Upload Disabled')
                ], max_length=25)),
                ('reason', models.TextField()),
                ('details', models.TextField(blank=True)),
                ('starts_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('lifted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                            related_name='suspensions', to='accounts.channel')),
                ('suspended_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                                 related_name='channel_suspensions_issued', to=settings.AUTH_USER_MODEL)),
                ('lifted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                              related_name='channel_suspensions_lifted', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]