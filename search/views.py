from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.db.models import Q, Count
from videos.models import Video
from accounts.models import Channel
from .models import SearchHistory, TrendingTopic, PopularSearch


class SearchView(ListView):
    """Main search view"""
    model = Video
    template_name = 'search/search.html'
    context_object_name = 'videos'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Video.objects.none()
        
        # Record search history
        if self.request.user.is_authenticated:
            SearchHistory.objects.create(
                user=self.request.user,
                query=query,
                results_count=0  # Will be updated after we get results
            )
        
        # Search in videos
        videos = Video.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query),
            visibility='public',
            processing_status='completed'
        ).order_by('-view_count', '-uploaded_at')
        
        return videos
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        context['query'] = query
        
        # Also search channels
        if query:
            context['channels'] = Channel.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )[:10]
        else:
            context['channels'] = []
        
        return context


class SearchSuggestionsView(TemplateView):
    """HTMX endpoint for search suggestions"""
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        suggestions = []
        
        if query and len(query) >= 2:
            # Get video title suggestions
            video_suggestions = Video.objects.filter(
                title__icontains=query,
                visibility='public',
                processing_status='completed'
            ).values_list('title', flat=True)[:5]
            
            # Get channel name suggestions
            channel_suggestions = Channel.objects.filter(
                name__icontains=query
            ).values_list('name', flat=True)[:3]
            
            suggestions = list(video_suggestions) + list(channel_suggestions)
        
        return JsonResponse({'suggestions': suggestions})


class AutocompleteView(TemplateView):
    """HTMX endpoint for search autocomplete"""
    template_name = 'search/autocomplete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        if query and len(query) >= 2:
            # Get popular searches that match
            popular_searches = PopularSearch.objects.filter(
                query__icontains=query
            ).order_by('-search_count')[:5]
            
            context['popular_searches'] = popular_searches
            context['query'] = query
        
        return context


class TrendingView(ListView):
    """Trending videos and topics"""
    model = Video
    template_name = 'search/trending.html'
    context_object_name = 'trending_videos'
    paginate_by = 24
    
    def get_queryset(self):
        # Get trending videos based on recent views and engagement
        return Video.objects.filter(
            visibility='public',
            processing_status='completed'
        ).order_by('-view_count', '-like_count', '-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get trending topics
        context['trending_topics'] = TrendingTopic.objects.filter(
            is_active=True
        ).order_by('-engagement_score')[:10]
        
        return context


class TrendingCategoryView(ListView):
    """Trending videos by category"""
    model = Video
    template_name = 'search/trending_category.html'
    context_object_name = 'videos'
    paginate_by = 24
    
    def get_queryset(self):
        category = self.kwargs.get('category')
        return Video.objects.filter(
            category=category,
            visibility='public',
            processing_status='completed'
        ).order_by('-view_count', '-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.kwargs.get('category')
        return context


class ExploreView(TemplateView):
    """Content exploration page"""
    template_name = 'search/explore.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get videos from different categories
        categories = ['entertainment', 'music', 'education', 'news', 'sports']
        context['category_videos'] = {}
        
        for category in categories:
            context['category_videos'][category] = Video.objects.filter(
                category=category,
                visibility='public',
                processing_status='completed'
            ).order_by('-view_count')[:8]
        
        # Get trending topics
        context['trending_topics'] = TrendingTopic.objects.filter(
            is_active=True
        ).order_by('-engagement_score')[:12]
        
        return context


class CategoryView(ListView):
    """Videos by specific category"""
    model = Video
    template_name = 'search/category.html'
    context_object_name = 'videos'
    paginate_by = 24
    
    def get_queryset(self):
        category = self.kwargs.get('category')
        return Video.objects.filter(
            category=category,
            visibility='public',
            processing_status='completed'
        ).order_by('-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.kwargs.get('category')
        context['category_title'] = dict(Video.CATEGORY_CHOICES).get(context['category'], context['category'])
        return context


class CategoriesView(TemplateView):
    """All categories overview"""
    template_name = 'search/categories.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get video count for each category
        category_stats = []
        for category_code, category_name in Video.CATEGORY_CHOICES:
            count = Video.objects.filter(
                category=category_code,
                visibility='public',
                processing_status='completed'
            ).count()
            
            if count > 0:
                category_stats.append({
                    'code': category_code,
                    'name': category_name,
                    'count': count
                })
        
        context['categories'] = sorted(category_stats, key=lambda x: x['count'], reverse=True)
        return context


class LanguageView(ListView):
    """Videos by language"""
    model = Video
    template_name = 'search/language.html'
    context_object_name = 'videos'
    paginate_by = 24
    
    def get_queryset(self):
        language = self.kwargs.get('language')
        return Video.objects.filter(
            language=language,
            visibility='public',
            processing_status='completed'
        ).order_by('-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['language'] = self.kwargs.get('language')
        return context


class PopularView(ListView):
    """Popular videos overall"""
    model = Video
    template_name = 'search/popular.html'
    context_object_name = 'videos'
    paginate_by = 24
    
    def get_queryset(self):
        return Video.objects.filter(
            visibility='public',
            processing_status='completed'
        ).order_by('-view_count')


class PopularTodayView(ListView):
    """Popular videos today"""
    model = Video
    template_name = 'search/popular_today.html'
    context_object_name = 'videos'
    paginate_by = 24
    
    def get_queryset(self):
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        return Video.objects.filter(
            visibility='public',
            processing_status='completed',
            uploaded_at__date=today
        ).order_by('-view_count')


class PopularWeekView(ListView):
    """Popular videos this week"""
    model = Video
    template_name = 'search/popular_week.html'
    context_object_name = 'videos'
    paginate_by = 24
    
    def get_queryset(self):
        from django.utils import timezone
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        return Video.objects.filter(
            visibility='public',
            processing_status='completed',
            uploaded_at__gte=week_ago
        ).order_by('-view_count')


class RegionalView(TemplateView):
    """Regional content overview"""
    template_name = 'search/regional.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get videos by different Indian languages
        languages = ['hi', 'ta', 'te', 'bn', 'mr', 'gu', 'kn', 'ml', 'pa']
        context['language_videos'] = {}
        
        for lang in languages:
            context['language_videos'][lang] = Video.objects.filter(
                language=lang,
                visibility='public',
                processing_status='completed'
            ).order_by('-view_count')[:6]
        
        return context


class RegionalContentView(ListView):
    """Regional content by specific region"""
    model = Video
    template_name = 'search/regional_content.html'
    context_object_name = 'videos'
    paginate_by = 24
    
    def get_queryset(self):
        region = self.kwargs.get('region')
        
        # Map region to language codes
        region_language_map = {
            'hindi': 'hi',
            'tamil': 'ta',
            'telugu': 'te',
            'bengali': 'bn',
            'marathi': 'mr',
            'gujarati': 'gu',
            'kannada': 'kn',
            'malayalam': 'ml',
            'punjabi': 'pa'
        }
        
        language = region_language_map.get(region.lower(), 'en')
        
        return Video.objects.filter(
            language=language,
            visibility='public',
            processing_status='completed'
        ).order_by('-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['region'] = self.kwargs.get('region')
        return context
