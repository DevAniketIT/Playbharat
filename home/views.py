from django.shortcuts import render
from django.views.generic import ListView
from videos.models import Video

class HomeView(ListView):
    model = Video
    template_name = 'home/home.html'
    context_object_name = 'videos'
    paginate_by = 12
    
    def get_queryset(self):
        # Get public videos that are processed
        return Video.objects.filter(
            visibility='public', 
            processing_status='completed'
        ).order_by('-published_at', '-uploaded_at')[:12]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add categories for filtering
        context['categories'] = [
            {'name': 'Entertainment', 'slug': 'entertainment', 'icon': 'film'},
            {'name': 'Music', 'slug': 'music', 'icon': 'music-note-beamed'},
            {'name': 'Education', 'slug': 'education', 'icon': 'book'},
            {'name': 'News', 'slug': 'news', 'icon': 'newspaper'},
            {'name': 'Sports', 'slug': 'sports', 'icon': 'trophy'},
            {'name': 'Gaming', 'slug': 'gaming', 'icon': 'controller'},
            {'name': 'Cooking', 'slug': 'cooking', 'icon': 'egg-fried'},
        ]
        
        # Add trending videos (for now, just most viewed)
        context['trending_videos'] = Video.objects.filter(
            visibility='public', 
            processing_status='completed'
        ).order_by('-view_count')[:5]
        
        return context

def home(request):
    """Simplified functional view alternative"""
    try:
        videos = Video.objects.filter(
            visibility='public',
            processing_status='completed'
        ).order_by('-published_at', '-uploaded_at')[:12]
        
        trending_videos = Video.objects.filter(
            visibility='public',
            processing_status='completed'
        ).order_by('-view_count')[:5]
        
        # Ensure we always have lists, not None
        videos = list(videos) if videos else []
        trending_videos = list(trending_videos) if trending_videos else []
        
    except Exception as e:
        # Fallback to empty lists if database query fails
        videos = []
        trending_videos = []
    
    categories = [
        {'name': 'Entertainment', 'slug': 'entertainment', 'icon': 'film'},
        {'name': 'Music', 'slug': 'music', 'icon': 'music-note-beamed'},
        {'name': 'Education', 'slug': 'education', 'icon': 'book'},
        {'name': 'News', 'slug': 'news', 'icon': 'newspaper'},
        {'name': 'Sports', 'slug': 'sports', 'icon': 'trophy'},
        {'name': 'Gaming', 'slug': 'gaming', 'icon': 'controller'},
        {'name': 'Cooking', 'slug': 'cooking', 'icon': 'egg-fried'},
    ]
    
    context = {
        'videos': videos,
        'trending_videos': trending_videos,
        'categories': categories,
    }
    
    return render(request, 'home/home.html', context)
