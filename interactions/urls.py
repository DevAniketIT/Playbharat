from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    # Comment system (HTMX powered - ONLY EXISTING VIEWS)
    path('comment/add/', views.AddCommentView.as_view(), name='add_comment'),
    path('comment/<uuid:pk>/reply/', views.ReplyCommentView.as_view(), name='reply_comment'),
    path('comment/<uuid:pk>/edit/', views.EditCommentView.as_view(), name='edit_comment'),
    path('comment/<uuid:pk>/delete/', views.DeleteCommentView.as_view(), name='delete_comment'),
    path('comment/<uuid:pk>/like/', views.LikeCommentView.as_view(), name='like_comment'),
    
    # Video interactions (LIMITED TO EXISTING)
    path('video/<uuid:pk>/like/', views.LikeVideoView.as_view(), name='like_video'),
    path('video/<uuid:pk>/share/', views.ShareVideoView.as_view(), name='share_video'),
    
    # Additional essential features
    path('video/<uuid:pk>/report/', views.ReportVideoView.as_view(), name='report_video'),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', views.UnsubscribeView.as_view(), name='unsubscribe'),
    path('subscriptions/', views.SubscriptionsView.as_view(), name='subscriptions'),
    path('history/', views.WatchHistoryView.as_view(), name='watch_history'),
    path('history/clear/', views.ClearHistoryView.as_view(), name='clear_history'),
    path('liked-videos/', views.LikedVideosView.as_view(), name='liked_videos'),
    # path('playlists/', views.PlaylistListView.as_view(), name='playlist_list'),
    # path('playlists/create/', views.CreatePlaylistView.as_view(), name='create_playlist'),
    # path('playlists/<uuid:pk>/', views.PlaylistDetailView.as_view(), name='playlist_detail'),
    # path('playlists/<uuid:pk>/edit/', views.PlaylistEditView.as_view(), name='playlist_edit'),
    # path('followers/', views.FollowerListView.as_view(), name='follower_list'),
    # path('following/', views.FollowingListView.as_view(), name='following_list'),
    # path('follow/<str:username>/', views.FollowUserView.as_view(), name='follow_user'),
    # path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    # path('notifications/settings/', views.NotificationSettingsView.as_view(), name='notification_settings'),
    # path('activity/', views.ActivityFeedView.as_view(), name='activity_feed'),
    # path('dashboard/', views.InteractionDashboardView.as_view(), name='dashboard'),
    # path('reports/', views.MyReportsView.as_view(), name='my_reports'),
    # path('report/<uuid:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    # path('api/toggle-like/', views.ToggleLikeAPIView.as_view(), name='api_toggle_like'),
    # path('api/toggle-follow/', views.ToggleFollowAPIView.as_view(), name='api_toggle_follow'),
    # path('api/load-comments/', views.LoadCommentsAPIView.as_view(), name='api_load_comments'),
    # path('api/notification-count/', views.NotificationCountAPIView.as_view(), name='api_notification_count'),
]
