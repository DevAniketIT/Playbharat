from django.urls import path
from . import views
# from . import api_views  # Comment out until api_views is fixed

app_name = 'videos'

urlpatterns = [
    # Video browsing
    path('', views.VideoListView.as_view(), name='list'),
    
    # Video upload and management
    path('upload/', views.VideoUploadView.as_view(), name='upload'),
    path('manage/', views.ManageVideosView.as_view(), name='manage'),
    path('edit/<uuid:pk>/', views.VideoEditView.as_view(), name='edit'),
    path('delete/<uuid:pk>/', views.VideoDeleteView.as_view(), name='delete'),
    # 
    # Video viewing
    path('watch/<slug:slug>/', views.VideoDetailView.as_view(), name='watch'),
    # 
    # # Playlists
    # path('playlists/', views.PlaylistListView.as_view(), name='playlist_list'),
    # path('playlists/create/', views.CreatePlaylistView.as_view(), name='create_playlist'),
    # path('playlist/<uuid:pk>/', views.PlaylistDetailView.as_view(), name='playlist_detail'),
    # path('playlist/<uuid:pk>/edit/', views.EditPlaylistView.as_view(), name='edit_playlist'),
    # 
    # # Video Actions
    # path('<uuid:pk>/like/', views.VideoLikeView.as_view(), name='like'),
    # path('<uuid:pk>/report/', views.VideoReportView.as_view(), name='report'),
    # path('<uuid:pk>/share/', views.VideoShareView.as_view(), name='share'),
    # 
    # # Comments
    # path('<uuid:pk>/comments/', views.CommentListView.as_view(), name='comments'),
    # path('<uuid:pk>/comments/add/', views.CommentCreateView.as_view(), name='comment_create'),
    # path('comments/<int:comment_pk>/edit/', views.CommentEditView.as_view(), name='comment_edit'),
    # path('comments/<int:comment_pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    # 
    # Browse & Discovery
    path('trending/', views.TrendingVideosView.as_view(), name='trending'),
    # path('category/<str:category>/', views.CategoryVideosView.as_view(), name='category'),
    # path('recent/', views.RecentVideosView.as_view(), name='recent'),
    # 
    # # Watchlist & History
    # path('watchlist/', views.WatchlistView.as_view(), name='watchlist'),
    # path('history/', views.WatchHistoryView.as_view(), name='history'),
    # 
    # # HTMX/API endpoints
    # path('upload/progress/', views.UploadProgressView.as_view(), name='upload_progress'),
    # path('<uuid:pk>/add-to-playlist/', views.AddToPlaylistView.as_view(), name='add_to_playlist'),
    # path('api/<uuid:pk>/toggle-like/', views.ToggleLikeView.as_view(), name='toggle_like'),
    # path('api/<uuid:pk>/increment-view/', views.IncrementViewView.as_view(), name='increment_view'),
    # path('api/video-suggestions/', views.VideoSuggestionsView.as_view(), name='video_suggestions'),
    
    # Additional HTMX API endpoints - disabled until api_views is fixed
    # path('api/<uuid:pk>/like/', api_views.VideoLikeAPIView.as_view(), name='api_video_like'),
    # path('api/<uuid:pk>/comment/', api_views.VideoCommentAPIView.as_view(), name='api_video_comment'),
    # path('api/<uuid:pk>/comments/', api_views.LoadCommentsAPIView.as_view(), name='api_load_comments'),
    # path('api/search-suggestions/', api_views.VideoSearchSuggestionsAPIView.as_view(), name='api_search_suggestions'),
    # path('api/trending/', api_views.TrendingVideosAPIView.as_view(), name='api_trending'),
    # path('api/recommendations/', api_views.VideoRecommendationsAPIView.as_view(), name='api_recommendations'),
]
