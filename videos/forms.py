from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field
from crispy_forms.bootstrap import FormActions
from .models import Video, Playlist


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            'title', 'description', 'video_file', 'thumbnail', 'category', 
            'language', 'tags', 'visibility', 'age_restriction', 
            'allow_comments', 'allow_likes'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell viewers about your video'}),
            'tags': forms.TextInput(attrs={'placeholder': 'comedy, entertainment, funny (separate with commas)'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter an engaging title'}),
            'video_file': forms.FileInput(attrs={'accept': 'video/*'}),
            'thumbnail': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4 class="mb-3"><i class="bi bi-film me-2"></i>Video Details</h4>'),
            'title',
            'description',
            HTML('<h5 class="mt-4 mb-3">Media Files</h5>'),
            Row(
                Column('video_file', css_class='form-group col-md-8'),
                Column('thumbnail', css_class='form-group col-md-4'),
            ),
            HTML('<h5 class="mt-4 mb-3">Categorization</h5>'),
            Row(
                Column('category', css_class='form-group col-md-6'),
                Column('language', css_class='form-group col-md-6'),
            ),
            'tags',
            HTML('<h5 class="mt-4 mb-3">Privacy & Settings</h5>'),
            Row(
                Column('visibility', css_class='form-group col-md-6'),
                Column(
                    Field('age_restriction', wrapper_class='form-check'),
                    css_class='form-group col-md-6'
                ),
            ),
            Row(
                Column(
                    Field('allow_comments', wrapper_class='form-check'),
                    css_class='form-group col-md-6'
                ),
                Column(
                    Field('allow_likes', wrapper_class='form-check'),
                    css_class='form-group col-md-6'
                ),
            ),
            FormActions(
                Submit('submit', 'Upload Video', css_class='btn btn-success btn-lg')
            )
        )

    def clean_video_file(self):
        video = self.cleaned_data.get('video_file')
        if video:
            # Check file size (max 2GB)
            if video.size > 2 * 1024 * 1024 * 1024:
                raise forms.ValidationError('Video file too large. Maximum size is 2GB.')
            
            # Check file type
            allowed_types = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv']
            if video.content_type not in allowed_types:
                raise forms.ValidationError('Unsupported video format.')
        
        return video

    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail:
            # Check file size (max 5MB)
            if thumbnail.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Thumbnail too large. Maximum size is 5MB.')
        
        return thumbnail


class VideoEditForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            'title', 'description', 'thumbnail', 'category', 'tags', 
            'visibility', 'age_restriction', 'allow_comments', 'allow_likes'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'placeholder': 'Separate tags with commas'}),
            'thumbnail': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            'thumbnail',
            Row(
                Column('category', css_class='form-group col-md-6'),
                Column('visibility', css_class='form-group col-md-6'),
            ),
            'tags',
            Row(
                Column(
                    Field('age_restriction', wrapper_class='form-check'),
                    css_class='form-group col-md-4'
                ),
                Column(
                    Field('allow_comments', wrapper_class='form-check'),
                    css_class='form-group col-md-4'
                ),
                Column(
                    Field('allow_likes', wrapper_class='form-check'),
                    css_class='form-group col-md-4'
                ),
            ),
            FormActions(
                Submit('submit', 'Save Changes', css_class='btn btn-primary')
            )
        )


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['title', 'description', 'visibility']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your playlist'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter playlist title'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            'visibility',
            FormActions(
                Submit('submit', 'Create Playlist', css_class='btn btn-primary')
            )
        )


# CommentForm will be implemented when Comment model is created
# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['content']
#         widgets = {
#             'content': forms.Textarea(attrs={
#                 'rows': 3,
#                 'placeholder': 'Add a comment...',
#                 'class': 'form-control'
#             }),
#         }
# 
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_show_labels = False
#         self.helper.layout = Layout(
#             'content',
#             FormActions(
#                 Submit('submit', 'Comment', css_class='btn btn-primary btn-sm')
#             )
#         )


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search videos, channels, creators...',
            'class': 'form-control',
            'autocomplete': 'off'
        }),
        label='Search'
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + Video.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    duration = forms.ChoiceField(
        choices=[
            ('', 'Any Duration'),
            ('short', 'Under 4 minutes'),
            ('medium', '4-20 minutes'),
            ('long', 'Over 20 minutes'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    upload_date = forms.ChoiceField(
        choices=[
            ('', 'Any Time'),
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('year', 'This Year'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('relevance', 'Relevance'),
            ('upload_date', 'Upload Date'),
            ('view_count', 'View Count'),
            ('rating', 'Rating'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('q', css_class='form-group col-md-12'),
            ),
            Row(
                Column('category', css_class='form-group col-md-3'),
                Column('duration', css_class='form-group col-md-3'),
                Column('upload_date', css_class='form-group col-md-3'),
                Column('sort_by', css_class='form-group col-md-3'),
            ),
            FormActions(
                Submit('submit', 'Search', css_class='btn btn-primary')
            )
        )


class ReportContentForm(forms.Form):
    REASON_CHOICES = [
        ('spam', 'Spam or misleading'),
        ('harassment', 'Harassment or bullying'),
        ('hate', 'Hate speech'),
        ('violence', 'Violence or dangerous content'),
        ('copyright', 'Copyright infringement'),
        ('privacy', 'Privacy violation'),
        ('other', 'Other'),
    ]

    reason = forms.ChoiceField(choices=REASON_CHOICES, widget=forms.RadioSelect)
    description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional details (optional)'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Why are you reporting this content?</h5>'),
            'reason',
            'description',
            FormActions(
                Submit('submit', 'Submit Report', css_class='btn btn-danger')
            )
        )