from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field, Div
from crispy_forms.bootstrap import FormActions, AccordionGroup, Accordion
from .models import Channel


class ChannelCreateForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = [
            'name', 'handle', 'description', 'category', 'language', 
            'banner', 'avatar', 'trailer_video'
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Tell viewers about your channel and what they can expect from your content'
            }),
            'name': forms.TextInput(attrs={'placeholder': 'Enter your channel name'}),
            'handle': forms.TextInput(attrs={'placeholder': '@yourchannel'}),
            'banner': forms.FileInput(attrs={'accept': 'image/*'}),
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="mb-4">'),
            HTML('<h4><i class="bi bi-broadcast me-2"></i>Create Your Channel</h4>'),
            HTML('<p class="text-muted">Set up your channel to start sharing content with the world</p>'),
            HTML('</div>'),
            
            HTML('<h5 class="mt-4 mb-3">Channel Identity</h5>'),
            'name',
            'handle',
            'description',
            
            HTML('<h5 class="mt-4 mb-3">Channel Details</h5>'),
            Row(
                Column('category', css_class='form-group col-md-6'),
                Column('language', css_class='form-group col-md-6'),
            ),
            
            HTML('<h5 class="mt-4 mb-3">Channel Branding</h5>'),
            HTML('<div class="alert alert-info">'),
            HTML('<small><i class="bi bi-info-circle me-1"></i>Avatar: 800x800px recommended | Banner: 2560x1440px recommended</small>'),
            HTML('</div>'),
            Row(
                Column('avatar', css_class='form-group col-md-6'),
                Column('banner', css_class='form-group col-md-6'),
            ),
            'trailer_video',
            
            FormActions(
                Submit('submit', 'Create Channel', css_class='btn btn-success btn-lg')
            )
        )

    def clean_handle(self):
        handle = self.cleaned_data.get('handle')
        if handle:
            # Ensure handle starts with @
            if not handle.startswith('@'):
                handle = '@' + handle
            
            # Check if handle already exists
            if Channel.objects.filter(handle=handle).exists():
                raise forms.ValidationError('This handle is already taken.')
            
            # Validate handle format
            import re
            if not re.match(r'^@[a-zA-Z0-9_]{3,30}$', handle):
                raise forms.ValidationError(
                    'Handle must be 3-30 characters long and contain only letters, numbers, and underscores.'
                )
        
        return handle

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Check file size (max 2MB)
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Avatar too large. Maximum size is 2MB.')
        
        return avatar

    def clean_banner(self):
        banner = self.cleaned_data.get('banner')
        if banner:
            # Check file size (max 5MB)
            if banner.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Banner too large. Maximum size is 5MB.')
        
        return banner


class ChannelEditForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = [
            'name', 'description', 'category', 'language', 
            'banner', 'avatar', 'trailer_video'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'banner': forms.FileInput(attrs={'accept': 'image/*'}),
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4 class="mb-3">Edit Channel</h4>'),
            
            Accordion(
                AccordionGroup(
                    'Basic Information',
                    'name',
                    'description',
                    Row(
                        Column('category', css_class='form-group col-md-6'),
                        Column('language', css_class='form-group col-md-6'),
                    ),
                ),
                AccordionGroup(
                    'Channel Art',
                    HTML('<div class="alert alert-info mb-3">'),
                    HTML('<small><i class="bi bi-info-circle me-1"></i>Leave empty to keep current images</small>'),
                    HTML('</div>'),
                    Row(
                        Column('avatar', css_class='form-group col-md-6'),
                        Column('banner', css_class='form-group col-md-6'),
                    ),
                ),
                AccordionGroup(
                    'Channel Trailer',
                    'trailer_video',
                ),
            ),
            
            FormActions(
                Submit('submit', 'Save Changes', css_class='btn btn-primary')
            )
        )

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Avatar too large. Maximum size is 2MB.')
        return avatar

    def clean_banner(self):
        banner = self.cleaned_data.get('banner')
        if banner:
            if banner.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Banner too large. Maximum size is 5MB.')
        return banner


class ChannelSettingsForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ['visibility', 'allow_comments', 'allow_subscriptions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Channel Privacy & Interaction</h5>'),
            'visibility',
            Row(
                Column(
                    Field('allow_comments', wrapper_class='form-check'),
                    css_class='form-group col-md-6'
                ),
                Column(
                    Field('allow_subscriptions', wrapper_class='form-check'),
                    css_class='form-group col-md-6'
                ),
            ),
            FormActions(
                Submit('submit', 'Update Settings', css_class='btn btn-primary')
            )
        )


class ChannelAnalyticsFilterForm(forms.Form):
    date_range = forms.ChoiceField(
        choices=[
            ('7', 'Last 7 days'),
            ('30', 'Last 30 days'),
            ('90', 'Last 3 months'),
            ('365', 'Last year'),
            ('all', 'All time'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    metric = forms.ChoiceField(
        choices=[
            ('views', 'Views'),
            ('subscribers', 'Subscribers'),
            ('watch_time', 'Watch Time'),
            ('engagement', 'Engagement'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('date_range', css_class='form-group col-md-6'),
                Column('metric', css_class='form-group col-md-6'),
            ),
            FormActions(
                Submit('submit', 'Apply Filter', css_class='btn btn-outline-primary')
            )
        )


class ChannelSearchForm(forms.Form):
    q = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search channels by name, handle, or category...',
            'class': 'form-control',
            'autocomplete': 'off'
        }),
        label='Search Channels'
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + Channel.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    language = forms.ChoiceField(
        choices=[('', 'All Languages')] + Channel.LANGUAGE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('subscribers', 'Most Subscribers'),
            ('recent', 'Recently Created'),
            ('active', 'Most Active'),
            ('name', 'Alphabetical'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            'q',
            Row(
                Column('category', css_class='form-group col-md-4'),
                Column('language', css_class='form-group col-md-4'),
                Column('sort_by', css_class='form-group col-md-4'),
            ),
            FormActions(
                Submit('submit', 'Search', css_class='btn btn-primary')
            )
        )


class ChannelCollaborationForm(forms.Form):
    collaborator_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter collaborator email',
            'class': 'form-control'
        })
    )
    role = forms.ChoiceField(
        choices=[
            ('editor', 'Editor - Can upload and edit videos'),
            ('moderator', 'Moderator - Can manage comments and community'),
            ('analyst', 'Analyst - Can view analytics only'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    message = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Optional message to the collaborator'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Invite Collaborator</h5>'),
            'collaborator_email',
            'role',
            'message',
            FormActions(
                Submit('submit', 'Send Invitation', css_class='btn btn-success')
            )
        )