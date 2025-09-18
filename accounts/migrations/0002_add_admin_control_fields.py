# Generated manually for PlayBharat admin control system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Add admin control fields to User model
        migrations.AddField(
            model_name='user',
            name='is_banned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='ban_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='banned_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='banned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                  related_name='users_banned', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='is_suspended',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='suspension_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='suspension_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_warned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='warning_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='warning_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='can_upload',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='can_comment',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='can_like',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='strike_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='last_strike_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='admin_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='last_activity',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='requires_manual_review',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='review_reason',
            field=models.TextField(blank=True),
        ),
        
        # Add admin control fields to Channel model
        migrations.AddField(
            model_name='channel',
            name='is_suspended',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='channel',
            name='suspension_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='suspended_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                  related_name='channels_suspended', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='channel',
            name='suspended_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='suspension_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='is_under_review',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='channel',
            name='review_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='reviewer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                  related_name='channels_reviewing', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='channel',
            name='strike_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='channel',
            name='warning_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='channel',
            name='can_upload',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='can_livestream',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='can_monetize',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='channel',
            name='admin_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='compliance_score',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='channel',
            name='requires_manual_approval',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='channel',
            name='auto_moderation_enabled',
            field=models.BooleanField(default=True),
        ),
    ]