from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field, Div
from crispy_forms.bootstrap import FormActions


class VideoPlayerSettingsForm(forms.Form):
    """Form for video player preferences and settings"""
    
    QUALITY_CHOICES = [
        ('auto', 'Auto (recommended)'),
        ('144p', '144p'),
        ('240p', '240p'),
        ('360p', '360p'),
        ('480p', '480p'),
        ('720p', '720p (HD)'),
        ('1080p', '1080p (Full HD)'),
        ('1440p', '1440p (2K)'),
        ('2160p', '2160p (4K)'),
    ]
    
    PLAYBACK_SPEED_CHOICES = [
        ('0.25', '0.25x'),
        ('0.5', '0.5x'),
        ('0.75', '0.75x'),
        ('1', '1x (Normal)'),
        ('1.25', '1.25x'),
        ('1.5', '1.5x'),
        ('1.75', '1.75x'),
        ('2', '2x'),
    ]
    
    default_quality = forms.ChoiceField(
        choices=QUALITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    default_speed = forms.ChoiceField(
        choices=PLAYBACK_SPEED_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    autoplay = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    theater_mode = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    show_captions = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    volume = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=80,
        widget=forms.RangeInput(attrs={'class': 'form-range'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5><i class="bi bi-gear me-2"></i>Player Settings</h5>'),
            Row(
                Column('default_quality', css_class='form-group col-md-6'),
                Column('default_speed', css_class='form-group col-md-6'),
            ),
            Row(
                Column(
                    Field('autoplay', wrapper_class='form-check'),
                    css_class='form-group col-md-6'
                ),
                Column(
                    Field('theater_mode', wrapper_class='form-check'),
                    css_class='form-group col-md-6'
                ),
            ),
            Field('show_captions', wrapper_class='form-check'),
            HTML('<label for="id_volume" class="form-label">Default Volume</label>'),
            'volume',
            FormActions(
                Submit('submit', 'Save Settings', css_class='btn btn-primary')
            )
        )


class WatchlistForm(forms.Form):
    """Form for adding videos to watchlist or playlists"""
    
    action = forms.ChoiceField(
        choices=[
            ('watch_later', 'Watch Later'),
            ('add_to_playlist', 'Add to Playlist'),
            ('remove_from_watchlist', 'Remove from Watchlist'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    playlist_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'action',
            'playlist_id',
            FormActions(
                Submit('submit', 'Add to List', css_class='btn btn-success')
            )
        )


class VideoRatingForm(forms.Form):
    """Form for rating videos (like/dislike)"""
    
    RATING_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('neutral', 'Remove Rating'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False


class VideoShareForm(forms.Form):
    """Form for sharing videos"""
    
    SHARE_METHODS = [
        ('link', 'Copy Link'),
        ('email', 'Email'),
        ('social', 'Social Media'),
        ('embed', 'Embed Code'),
    ]
    
    method = forms.ChoiceField(
        choices=SHARE_METHODS,
        widget=forms.RadioSelect
    )
    
    start_time = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'mm:ss (e.g., 1:30)',
            'class': 'form-control'
        })
    )
    
    message = forms.CharField(
        required=False,
        max_length=280,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Add a message (optional)',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Share Video</h5>'),
            'method',
            'start_time',
            'message',
            FormActions(
                Submit('submit', 'Share', css_class='btn btn-primary')
            )
        )


class VideoReportForm(forms.Form):
    """Form for reporting inappropriate videos"""
    
    REPORT_REASONS = [
        ('spam', 'Spam or misleading'),
        ('violence', 'Violence or dangerous content'),
        ('harassment', 'Harassment or bullying'),
        ('hate', 'Hate speech'),
        ('adult', 'Adult content'),
        ('copyright', 'Copyright infringement'),
        ('privacy', 'Privacy violation'),
        ('other', 'Other'),
    ]
    
    reason = forms.ChoiceField(
        choices=REPORT_REASONS,
        widget=forms.RadioSelect
    )
    
    timestamp = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'mm:ss (if specific to a moment)',
            'class': 'form-control'
        })
    )
    
    description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Additional details (optional)',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5 class="text-danger">Report Video</h5>'),
            HTML('<p class="text-muted">Help us understand what\'s happening</p>'),
            'reason',
            'timestamp',
            'description',
            FormActions(
                Submit('submit', 'Submit Report', css_class='btn btn-danger')
            )
        )


class LiveChatForm(forms.Form):
    """Form for live chat during streaming"""
    
    message = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Say something...',
            'class': 'form-control',
            'autocomplete': 'off'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                'message',
                Submit('submit', 'Send', css_class='btn btn-primary btn-sm'),
                css_class='input-group'
            )
        )


class StreamingQualityForm(forms.Form):
    """Form for adjusting streaming quality preferences"""
    
    QUALITY_PREFERENCES = [
        ('data_saver', 'Data Saver (Lower quality, less data)'),
        ('auto', 'Auto (Recommended)'),
        ('higher_quality', 'Higher Quality (Uses more data)'),
    ]
    
    CONNECTION_CHOICES = [
        ('wifi', 'Wi-Fi'),
        ('mobile', 'Mobile Data'),
        ('auto', 'Auto-detect'),
    ]
    
    quality_preference = forms.ChoiceField(
        choices=QUALITY_PREFERENCES,
        widget=forms.RadioSelect
    )
    
    connection_type = forms.ChoiceField(
        choices=CONNECTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    limit_mobile_data = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Streaming Quality Settings</h5>'),
            'quality_preference',
            'connection_type',
            Field('limit_mobile_data', wrapper_class='form-check'),
            FormActions(
                Submit('submit', 'Save Preferences', css_class='btn btn-primary')
            )
        )


class VideoBookmarkForm(forms.Form):
    """Form for bookmarking specific timestamps in videos"""
    
    timestamp = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'mm:ss',
            'class': 'form-control'
        })
    )
    
    note = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Add a note for this bookmark',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h6>Bookmark This Moment</h6>'),
            'timestamp',
            'note',
            FormActions(
                Submit('submit', 'Save Bookmark', css_class='btn btn-success btn-sm')
            )
        )

    def clean_timestamp(self):
        timestamp = self.cleaned_data.get('timestamp')
        if timestamp:
            # Validate timestamp format (mm:ss or h:mm:ss)
            import re
            if not re.match(r'^(\d{1,2}:)?([0-5]?\d):([0-5]\d)$', timestamp):
                raise forms.ValidationError('Please enter a valid timestamp (mm:ss or h:mm:ss)')
        return timestamp


class ContinueWatchingForm(forms.Form):
    """Form for managing continue watching preferences"""
    
    auto_continue = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    save_position = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h6>Continue Watching Settings</h6>'),
            Field('auto_continue', wrapper_class='form-check'),
            Field('save_position', wrapper_class='form-check'),
            FormActions(
                Submit('submit', 'Update Settings', css_class='btn btn-primary btn-sm')
            )
        )