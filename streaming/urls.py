from django.urls import path
from . import views

app_name = 'streaming'

urlpatterns = [
    # Video watching (ONLY EXISTING VIEWS)
    path('<slug:slug>/', views.WatchVideoView.as_view(), name='watch'),
    path('<slug:slug>/embed/', views.EmbedVideoView.as_view(), name='embed'),
    
    # Video serving
    path('serve/<uuid:video_id>/<str:quality>/', views.ServeVideoView.as_view(), name='serve_video'),
    path('thumbnail/<uuid:video_id>/', views.ServeThumbnailView.as_view(), name='serve_thumbnail'),
    
    # Analytics endpoints (HTMX)
    path('track/view/', views.TrackViewView.as_view(), name='track_view'),
    path('track/engagement/', views.TrackEngagementView.as_view(), name='track_engagement'),
    
    # Live streaming (LIMITED TO EXISTING VIEWS)
    path('live/<uuid:stream_id>/', views.LiveStreamView.as_view(), name='live_stream'),
    path('live/<uuid:stream_id>/chat/', views.LiveChatView.as_view(), name='live_chat'),
    
    # DISABLED - Views don't exist:
    # path('player/settings/', views.PlayerSettingsView.as_view(), name='player_settings'),
    # path('quality/<slug:slug>/', views.VideoQualityView.as_view(), name='video_quality'),
    # path('captions/<slug:slug>/', views.VideoCaptionsView.as_view(), name='video_captions'),
    # path('watchlist/', views.WatchlistView.as_view(), name='watchlist'),
    # path('continue/', views.ContinueWatchingView.as_view(), name='continue_watching'),
    # path('history/', views.StreamingHistoryView.as_view(), name='history'),
    # path('bookmarks/', views.BookmarksView.as_view(), name='bookmarks'),
    # path('live/', views.LiveStreamListView.as_view(), name='live_list'),
    # path('api/update-position/', views.UpdatePositionAPIView.as_view(), name='api_update_position'),
    # path('api/player-stats/', views.PlayerStatsAPIView.as_view(), name='api_player_stats'),
    # path('api/watchlist-toggle/', views.WatchlistToggleAPIView.as_view(), name='api_watchlist_toggle'),
]
