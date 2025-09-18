from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field, Div
from crispy_forms.bootstrap import FormActions, Tab, TabHolder
from videos.models import Video
from channels.models import Channel


class AdvancedSearchForm(forms.Form):
    # Main search query
    q = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search videos, channels, creators...',
            'class': 'form-control form-control-lg',
            'autocomplete': 'off'
        }),
        label='Search Query',
        required=False
    )
    
    # Content type filter
    content_type = forms.ChoiceField(
        choices=[
            ('all', 'All Content'),
            ('videos', 'Videos Only'),
            ('channels', 'Channels Only'),
            ('playlists', 'Playlists Only'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    
    # Video specific filters
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + Video.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    language = forms.ChoiceField(
        choices=[('', 'All Languages')] + Video.LANGUAGE_CHOICES,
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
            ('hour', 'Last Hour'),
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('year', 'This Year'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Quality and features
    quality = forms.ChoiceField(
        choices=[
            ('', 'Any Quality'),
            ('hd', 'HD (720p+)'),
            ('4k', '4K'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    features = forms.MultipleChoiceField(
        choices=[
            ('subtitles', 'Subtitles/CC'),
            ('live', 'Live'),
            ('360', '360°'),
            ('vr', 'VR180'),
            ('hdr', 'HDR'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    # Sorting options
    sort_by = forms.ChoiceField(
        choices=[
            ('relevance', 'Relevance'),
            ('upload_date', 'Upload Date'),
            ('view_count', 'View Count'),
            ('rating', 'Rating'),
            ('title', 'Title A-Z'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            'q',
            HTML('<hr>'),
            
            TabHolder(
                Tab('Content Type',
                    'content_type',
                ),
                Tab('Video Filters',
                    Row(
                        Column('category', css_class='form-group col-md-6'),
                        Column('language', css_class='form-group col-md-6'),
                    ),
                    Row(
                        Column('duration', css_class='form-group col-md-6'),
                        Column('upload_date', css_class='form-group col-md-6'),
                    ),
                ),
                Tab('Quality & Features',
                    'quality',
                    HTML('<label class="form-label">Features</label>'),
                    'features',
                ),
                Tab('Sort Options',
                    'sort_by',
                ),
            ),
            
            HTML('<hr>'),
            FormActions(
                Submit('submit', 'Search', css_class='btn btn-primary btn-lg me-2'),
                HTML('<a href="{% url "search:index" %}" class="btn btn-outline-secondary">Clear All</a>')
            )
        )


class QuickSearchForm(forms.Form):
    q = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search...',
            'class': 'form-control',
            'autocomplete': 'off'
        }),
        label=''
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                'q',
                Submit('submit', 'Search', css_class='btn btn-primary'),
                css_class='input-group'
            )
        )


class SavedSearchForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter name for this search',
            'class': 'form-control'
        })
    )
    
    query = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    filters = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Save This Search</h5>'),
            'name',
            'query',
            'filters',
            FormActions(
                Submit('submit', 'Save Search', css_class='btn btn-success')
            )
        )


class SearchHistoryForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ('clear_all', 'Clear All History'),
            ('clear_selected', 'Clear Selected'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'action',
            FormActions(
                Submit('submit', 'Apply', css_class='btn btn-warning')
            )
        )


class SearchFilterForm(forms.Form):
    """Form for filtering search results without full search"""
    
    sort_by = forms.ChoiceField(
        choices=[
            ('relevance', 'Relevance'),
            ('upload_date', 'Upload Date'),
            ('view_count', 'View Count'),
            ('rating', 'Rating'),
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        required=False
    )
    
    duration = forms.ChoiceField(
        choices=[
            ('', 'Any Duration'),
            ('short', 'Under 4 minutes'),
            ('medium', '4-20 minutes'),
            ('long', 'Over 20 minutes'),
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        required=False
    )
    
    upload_date = forms.ChoiceField(
        choices=[
            ('', 'Any Time'),
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('year', 'This Year'),
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column('sort_by', css_class='form-group col-md-4'),
                Column('duration', css_class='form-group col-md-4'),
                Column('upload_date', css_class='form-group col-md-4'),
            )
        )


class SearchSuggestionsForm(forms.Form):
    """Form to handle search suggestions and autocomplete"""
    
    query = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
            'data-bs-toggle': 'dropdown'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_show_labels = False


class ReportSearchForm(forms.Form):
    """Form to report inappropriate search results or content"""
    
    REPORT_TYPES = [
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam Results'),
        ('broken', 'Broken Links'),
        ('copyright', 'Copyright Violation'),
        ('other', 'Other Issues'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        widget=forms.RadioSelect
    )
    
    description = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Please describe the issue in detail...'
        })
    )
    
    search_query = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    result_url = forms.URLField(
        widget=forms.HiddenInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h5>Report Search Issue</h5>'),
            'report_type',
            'description',
            'search_query',
            'result_url',
            FormActions(
                Submit('submit', 'Submit Report', css_class='btn btn-danger')
            )
        )