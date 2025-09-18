from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth import authenticate
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML, Div
from crispy_forms.bootstrap import FormActions, Tab, TabHolder, Accordion, AccordionGroup
from .models import User, Channel


class UserRegistrationForm(UserCreationForm):
    """User registration form with additional fields"""
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.'
    )
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    preferred_language = forms.ChoiceField(
        choices=User.LANGUAGE_CHOICES,
        initial='en',
        help_text='Choose your preferred language for the interface'
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'preferred_language', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h3 class="text-center mb-4">Join PlayBharat Family</h3>'),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            Field('username', css_class='form-group mb-3'),
            Field('email', css_class='form-group mb-3'),
            Field('preferred_language', css_class='form-group mb-3'),
            Field('password1', css_class='form-group mb-3'),
            Field('password2', css_class='form-group mb-3'),
            FormActions(
                Submit('register', 'Create Account', css_class='btn btn-primary w-100 mb-3'),
                HTML('<div class="text-center"><a href="{% url \'accounts:login\' %}" class="text-decoration-none">Already have an account? Login</a></div>')
            )
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.preferred_language = self.cleaned_data['preferred_language']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """User profile editing form"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'date_of_birth',
            'profile_picture', 'bio', 'preferred_language', 'country', 'state', 'city',
            'show_email', 'show_phone'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h3 class="mb-4">Edit Profile</h3>'),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
            ),
            Field('date_of_birth', css_class='form-group mb-3'),
            Field('profile_picture', css_class='form-group mb-3'),
            Field('bio', css_class='form-group mb-3'),
            Field('preferred_language', css_class='form-group mb-3'),
            Row(
                Column('country', css_class='form-group col-md-4 mb-3'),
                Column('state', css_class='form-group col-md-4 mb-3'),
                Column('city', css_class='form-group col-md-4 mb-3'),
            ),
            HTML('<h5 class="mt-4 mb-3">Privacy Settings</h5>'),
            Row(
                Column('show_email', css_class='form-group col-md-6 mb-3'),
                Column('show_phone', css_class='form-group col-md-6 mb-3'),
            ),
            FormActions(
                Submit('save', 'Save Changes', css_class='btn btn-primary me-2'),
                HTML('<a href="{% url \'accounts:profile\' %}" class="btn btn-outline-secondary">Cancel</a>')
            )
        )


class ChannelCreationForm(forms.ModelForm):
    """Channel creation and editing form"""
    
    class Meta:
        model = Channel
        fields = [
            'name', 'handle', 'description', 'category', 'avatar', 'banner',
            'website_url', 'twitter_url', 'instagram_url', 'facebook_url'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h3 class="mb-4">{% if form.instance.pk %}Edit Channel{% else %}Create Your Channel{% endif %}</h3>'),
            HTML('<div class="alert alert-info"><i class="bi bi-info-circle me-2"></i>Your channel is your space to share videos with the PlayBharat community.</div>'),
            Field('name', css_class='form-group mb-3'),
            Field('handle', css_class='form-group mb-3', placeholder='@yourchannel'),
            Field('description', css_class='form-group mb-3'),
            Field('category', css_class='form-group mb-3'),
            Row(
                Column('avatar', css_class='form-group col-md-6 mb-3'),
                Column('banner', css_class='form-group col-md-6 mb-3'),
            ),
            HTML('<h5 class="mt-4 mb-3">Social Links (Optional)</h5>'),
            Row(
                Column('website_url', css_class='form-group col-md-6 mb-3'),
                Column('twitter_url', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('instagram_url', css_class='form-group col-md-6 mb-3'),
                Column('facebook_url', css_class='form-group col-md-6 mb-3'),
            ),
            FormActions(
                Submit('save', '{% if form.instance.pk %}Update Channel{% else %}Create Channel{% endif %}', 
                      css_class='btn btn-primary me-2'),
                HTML('<a href="{% url \'accounts:channel_dashboard\' %}" class="btn btn-outline-secondary">Cancel</a>')
            )
        )

    def clean_handle(self):
        handle = self.cleaned_data['handle']
        if not handle.startswith('@'):
            handle = f'@{handle}'
        
        # Check if handle is unique (excluding current instance if editing)
        existing = Channel.objects.filter(handle=handle)
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise forms.ValidationError('This handle is already taken. Please choose another.')
        
        return handle

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError('Channel name must be at least 3 characters long.')
        return name


class LoginForm(forms.Form):
    """Custom login form with Bootstrap styling"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h3 class="text-center mb-4">Welcome Back to PlayBharat</h3>'),
            Field('username', css_class='form-group mb-3'),
            Field('password', css_class='form-group mb-3'),
            Field('remember_me', css_class='form-check mb-3'),
            FormActions(
                Submit('login', 'Login', css_class='btn btn-primary w-100 mb-3'),
                HTML('<div class="text-center">'),
                HTML('<a href="{% url \'accounts:register\' %}" class="text-decoration-none me-3">Create Account</a>'),
                HTML('<a href="#" class="text-decoration-none">Forgot Password?</a>'),
                HTML('</div>')
            )
        )


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with enhanced styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4><i class="bi bi-shield-lock me-2"></i>Change Password</h4>'),
            HTML('<p class="text-muted mb-4">Ensure your account is using a long, random password to stay secure.</p>'),
            'old_password',
            HTML('<hr class="my-4">'),
            'new_password1',
            'new_password2',
            FormActions(
                Submit('submit', 'Update Password', css_class='btn btn-primary')
            )
        )
        
        # Add Bootstrap classes to fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class AccountSettingsForm(forms.ModelForm):
    """Form for account settings and preferences"""
    
    class Meta:
        model = User
        fields = [
            'preferred_language', 'show_email', 'show_phone'
        ]
        widgets = {
            'show_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_phone': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4>Account Settings</h4>'),
            'preferred_language',
            HTML('<h6 class="mt-4">Profile Visibility</h6>'),
            Field('show_email', wrapper_class='form-check'),
            Field('show_phone', wrapper_class='form-check'),
            FormActions(
                Submit('submit', 'Save Settings', css_class='btn btn-primary')
            )
        )


class AccountDeactivationForm(forms.Form):
    """Form for account deactivation"""
    
    DEACTIVATION_REASONS = [
        ('privacy', 'Privacy concerns'),
        ('not_useful', 'Not useful anymore'),
        ('too_busy', 'Too busy / Too distracting'),
        ('technical_issues', 'Technical issues'),
        ('other', 'Other'),
    ]
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Enter your password to confirm'
    )
    
    reason = forms.ChoiceField(
        choices=DEACTIVATION_REASONS,
        widget=forms.RadioSelect,
        required=False
    )
    
    feedback = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Help us improve (optional)'
        })
    )
    
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I understand that deactivating my account will hide my profile and content'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="alert alert-danger">'),
            HTML('<h5 class="alert-heading">Deactivate Account</h5>'),
            HTML('<p>This will deactivate your account. You can reactivate it anytime by logging back in.</p>'),
            HTML('</div>'),
            'password',
            HTML('<h6 class="mt-4">Why are you leaving? (Optional)</h6>'),
            'reason',
            'feedback',
            Field('confirm', wrapper_class='form-check'),
            FormActions(
                Submit('submit', 'Deactivate Account', css_class='btn btn-danger')
            )
        )
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not authenticate(username=self.user.username, password=password):
            raise forms.ValidationError('Incorrect password.')
        return password


class TwoFactorSetupForm(forms.Form):
    """Form for setting up two-factor authentication"""
    
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890'
        }),
        help_text='Enter your phone number for SMS verification'
    )
    
    backup_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'backup@email.com'
        }),
        help_text='Optional backup email for recovery'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4><i class="bi bi-shield-check me-2"></i>Enable Two-Factor Authentication</h4>'),
            HTML('<p class="text-muted">Add an extra layer of security to your account.</p>'),
            'phone_number',
            'backup_email',
            FormActions(
                Submit('submit', 'Set Up 2FA', css_class='btn btn-success')
            )
        )


class ChannelAnalyticsPreferencesForm(forms.Form):
    """Form for channel analytics and reporting preferences"""
    
    public_subscriber_count = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Show subscriber count publicly on your channel'
    )
    
    public_view_count = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Show view counts on your videos'
    )
    
    analytics_sharing = forms.ChoiceField(
        choices=[
            ('private', 'Private (only me)'),
            ('collaborators', 'Collaborators only'),
            ('public', 'Public'),
        ],
        widget=forms.RadioSelect
    )
    
    weekly_reports = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Receive weekly analytics reports via email'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Channel Analytics Preferences</h5>'),
            HTML('<h6 class="mt-4">Public Display</h6>'),
            Field('public_subscriber_count', wrapper_class='form-check'),
            Field('public_view_count', wrapper_class='form-check'),
            HTML('<h6 class="mt-4">Analytics Sharing</h6>'),
            'analytics_sharing',
            HTML('<h6 class="mt-4">Reports</h6>'),
            Field('weekly_reports', wrapper_class='form-check'),
            FormActions(
                Submit('submit', 'Save Preferences', css_class='btn btn-primary')
            )
        )


class BulkUserActionsForm(forms.Form):
    """Form for admin bulk actions on users"""
    
    BULK_ACTIONS = [
        ('activate', 'Activate Selected'),
        ('deactivate', 'Deactivate Selected'),
        ('delete', 'Delete Selected'),
        ('export', 'Export Selected'),
    ]
    
    action = forms.ChoiceField(
        choices=BULK_ACTIONS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    selected_users = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I confirm this action'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'action',
            'selected_users',
            Field('confirm', wrapper_class='form-check'),
            FormActions(
                Submit('submit', 'Apply Action', css_class='btn btn-warning')
            )
        )
