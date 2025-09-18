from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field, Div
from crispy_forms.bootstrap import FormActions
from .models import Comment, Playlist, Like, Follow


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add a comment...',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            'content',
            FormActions(
                Submit('submit', 'Comment', css_class='btn btn-primary btn-sm')
            )
        )


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Write a reply...',
                'class': 'form-control form-control-sm'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            'content',
            FormActions(
                Submit('submit', 'Reply', css_class='btn btn-outline-primary btn-sm')
            )
        )


class CommentEditForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'content',
            FormActions(
                Submit('submit', 'Save Changes', css_class='btn btn-primary btn-sm me-2'),
                HTML('<button type="button" class="btn btn-secondary btn-sm" onclick="cancelEdit()">Cancel</button>')
            )
        )


class PlaylistCreateForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['title', 'description', 'visibility']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Describe your playlist (optional)'
            }),
            'title': forms.TextInput(attrs={'placeholder': 'Enter playlist title'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5><i class="bi bi-collection-play me-2"></i>Create New Playlist</h5>'),
            'title',
            'description',
            'visibility',
            FormActions(
                Submit('submit', 'Create Playlist', css_class='btn btn-success')
            )
        )


class PlaylistEditForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['title', 'description', 'visibility']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Edit Playlist</h5>'),
            'title',
            'description',
            'visibility',
            FormActions(
                Submit('submit', 'Save Changes', css_class='btn btn-primary')
            )
        )


class PlaylistAddVideoForm(forms.Form):
    """Form for adding videos to existing playlists"""
    
    playlist = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    create_new = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    new_playlist_title = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'New playlist name',
            'class': 'form-control'
        })
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['playlist'].queryset = Playlist.objects.filter(user=user)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h6>Add to Playlist</h6>'),
            'playlist',
            HTML('<hr class="my-3">'),
            Field('create_new', wrapper_class='form-check'),
            'new_playlist_title',
            FormActions(
                Submit('submit', 'Add Video', css_class='btn btn-success btn-sm')
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        create_new = cleaned_data.get('create_new')
        playlist = cleaned_data.get('playlist')
        new_playlist_title = cleaned_data.get('new_playlist_title')
        
        if create_new and not new_playlist_title:
            raise forms.ValidationError('Please enter a title for the new playlist.')
        
        if not create_new and not playlist:
            raise forms.ValidationError('Please select a playlist.')
        
        return cleaned_data


class LikeForm(forms.Form):
    """Form for liking/unliking content"""
    
    action = forms.ChoiceField(
        choices=[
            ('like', 'Like'),
            ('unlike', 'Unlike'),
        ],
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False


class FollowForm(forms.Form):
    """Form for following/unfollowing users or channels"""
    
    action = forms.ChoiceField(
        choices=[
            ('follow', 'Follow'),
            ('unfollow', 'Unfollow'),
        ],
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False


class ReportCommentForm(forms.Form):
    """Form for reporting inappropriate comments"""
    
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment or bullying'),
        ('hate', 'Hate speech'),
        ('violence', 'Threats of violence'),
        ('inappropriate', 'Inappropriate content'),
        ('other', 'Other'),
    ]
    
    reason = forms.ChoiceField(
        choices=REPORT_REASONS,
        widget=forms.RadioSelect
    )
    
    additional_info = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Additional details (optional)'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5 class="text-danger">Report Comment</h5>'),
            'reason',
            'additional_info',
            FormActions(
                Submit('submit', 'Submit Report', css_class='btn btn-danger')
            )
        )


class CommentModerationForm(forms.Form):
    """Form for comment moderation actions"""
    
    MODERATION_ACTIONS = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('delete', 'Delete'),
        ('pin', 'Pin Comment'),
        ('unpin', 'Unpin Comment'),
    ]
    
    action = forms.ChoiceField(
        choices=MODERATION_ACTIONS,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    reason = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Reason for action (optional)',
            'class': 'form-control form-control-sm'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column('action', css_class='form-group col-md-6'),
                Column('reason', css_class='form-group col-md-6'),
            ),
            FormActions(
                Submit('submit', 'Apply', css_class='btn btn-warning btn-sm')
            )
        )


class NotificationSettingsForm(forms.Form):
    """Form for managing interaction notifications"""
    
    email_on_comment = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    email_on_like = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    email_on_follow = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    email_on_reply = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    push_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Notification Preferences</h5>'),
            HTML('<h6 class="mt-3">Email Notifications</h6>'),
            Field('email_on_comment', wrapper_class='form-check'),
            Field('email_on_like', wrapper_class='form-check'),
            Field('email_on_follow', wrapper_class='form-check'),
            Field('email_on_reply', wrapper_class='form-check'),
            HTML('<h6 class="mt-3">Push Notifications</h6>'),
            Field('push_notifications', wrapper_class='form-check'),
            FormActions(
                Submit('submit', 'Save Preferences', css_class='btn btn-primary')
            )
        )


class BulkPlaylistActionForm(forms.Form):
    """Form for bulk actions on playlist items"""
    
    BULK_ACTIONS = [
        ('remove_selected', 'Remove Selected Videos'),
        ('move_to_top', 'Move to Top'),
        ('move_to_bottom', 'Move to Bottom'),
        ('copy_to_playlist', 'Copy to Another Playlist'),
    ]
    
    action = forms.ChoiceField(
        choices=BULK_ACTIONS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    target_playlist = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    selected_videos = forms.CharField(
        widget=forms.HiddenInput()
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target_playlist'].queryset = Playlist.objects.filter(user=user)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'action',
            'target_playlist',
            'selected_videos',
            FormActions(
                Submit('submit', 'Apply Action', css_class='btn btn-warning')
            )
        )


class SharePlaylistForm(forms.Form):
    """Form for sharing playlists"""
    
    SHARE_OPTIONS = [
        ('public', 'Make Public'),
        ('unlisted', 'Unlisted (link only)'),
        ('private', 'Private'),
    ]
    
    visibility = forms.ChoiceField(
        choices=SHARE_OPTIONS,
        widget=forms.RadioSelect
    )
    
    allow_collaboration = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    collaborator_emails = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Enter email addresses separated by commas'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Share Playlist</h5>'),
            'visibility',
            Field('allow_collaboration', wrapper_class='form-check'),
            'collaborator_emails',
            FormActions(
                Submit('submit', 'Update Sharing Settings', css_class='btn btn-primary')
            )
        )