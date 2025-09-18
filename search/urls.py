from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # Main Search (ONLY EXISTING VIEWS)
    path('', views.SearchView.as_view(), name='index'),
    
    # Search Features  
    path('suggestions/', views.SearchSuggestionsView.as_view(), name='suggestions'),
    path('autocomplete/', views.AutocompleteView.as_view(), name='autocomplete'),
    
    # Content discovery
    path('trending/', views.TrendingView.as_view(), name='trending'),
    path('trending/<str:category>/', views.TrendingCategoryView.as_view(), name='trending_category'),
    path('explore/', views.ExploreView.as_view(), name='explore'),
    
    # Category browsing
    path('category/<str:category>/', views.CategoryView.as_view(), name='category'),
    path('categories/', views.CategoriesView.as_view(), name='categories'),
    
    # DISABLED - Views don't exist:
    # path('results/', views.SearchResultsView.as_view(), name='results'),
    # path('advanced/', views.AdvancedSearchView.as_view(), name='advanced'),
    # path('videos/', views.VideoSearchView.as_view(), name='videos'),
    # path('channels/', views.ChannelSearchView.as_view(), name='channels'),
    # path('playlists/', views.PlaylistSearchView.as_view(), name='playlists'),
    # path('filters/', views.SearchFiltersView.as_view(), name='filters'),
    # path('history/', views.SearchHistoryView.as_view(), name='history'),
    # path('saved/', views.SavedSearchesView.as_view(), name='saved'),
    # path('api/suggestions/', views.SearchSuggestionsAPIView.as_view(), name='api_suggestions'),
    # path('api/autocomplete/', views.AutocompleteAPIView.as_view(), name='api_autocomplete'),
    # path('api/trending-terms/', views.TrendingTermsAPIView.as_view(), name='api_trending_terms'),
    # path('language/<str:language>/', views.LanguageView.as_view(), name='language'),
    # path('popular/', views.PopularView.as_view(), name='popular'),
    # path('popular/today/', views.PopularTodayView.as_view(), name='popular_today'),
    # path('popular/week/', views.PopularWeekView.as_view(), name='popular_week'),
    # path('regional/', views.RegionalView.as_view(), name='regional'),
    # path('regional/<str:region>/', views.RegionalContentView.as_view(), name='regional_content'),
]
