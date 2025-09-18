from django.urls import path
from . import views

app_name = 'channels'

urlpatterns = [
    # Channel Discovery
    path('', views.ChannelListView.as_view(), name='list'),
    path('browse/', views.ChannelBrowseView.as_view(), name='browse'),
    path('search/', views.ChannelSearchView.as_view(), name='search'),
    path('categories/', views.ChannelCategoriesView.as_view(), name='categories'),
    path('category/<str:category>/', views.ChannelCategoryView.as_view(), name='category'),
    
    # Channel Management (Creator Side)
    path('dashboard/', views.ChannelDashboardView.as_view(), name='dashboard'),
    path('create/', views.ChannelCreateView.as_view(), name='create'),
    path('edit/', views.ChannelEditView.as_view(), name='edit'),
    path('settings/', views.ChannelSettingsView.as_view(), name='settings'),
    path('analytics/', views.ChannelAnalyticsView.as_view(), name='analytics'),
    path('content/', views.ChannelContentView.as_view(), name='content'),
    path('community/', views.ChannelCommunityView.as_view(), name='community'),
    path('monetization/', views.ChannelMonetizationView.as_view(), name='monetization'),
    
    # Channel Public Pages
    path('<str:handle>/', views.ChannelDetailView.as_view(), name='detail'),
    path('<str:handle>/videos/', views.ChannelVideosView.as_view(), name='videos'),
    path('<str:handle>/playlists/', views.ChannelPlaylistsView.as_view(), name='playlists'),
    path('<str:handle>/about/', views.ChannelAboutView.as_view(), name='about'),
    path('<str:handle>/community/', views.ChannelCommunityPostsView.as_view(), name='community_posts'),
    
    # Channel Interactions
    path('<str:handle>/subscribe/', views.ChannelSubscribeView.as_view(), name='subscribe'),
    path('<str:handle>/unsubscribe/', views.ChannelUnsubscribeView.as_view(), name='unsubscribe'),
    path('<str:handle>/follow/', views.ChannelFollowView.as_view(), name='follow'),
    path('<str:handle>/report/', views.ChannelReportView.as_view(), name='report'),
    
    # Subscriptions Management
    path('subscriptions/', views.SubscriptionsView.as_view(), name='subscriptions'),
    path('subscriptions/manage/', views.ManageSubscriptionsView.as_view(), name='manage_subscriptions'),
    path('subscriptions/feed/', views.SubscriptionFeedView.as_view(), name='subscription_feed'),
    
    # Collaborations
    path('collaborations/', views.CollaborationsView.as_view(), name='collaborations'),
    path('collaborations/invite/', views.InviteCollaboratorView.as_view(), name='invite_collaborator'),
    path('collaborations/<int:pk>/accept/', views.AcceptCollaborationView.as_view(), name='accept_collaboration'),
    path('collaborations/<int:pk>/decline/', views.DeclineCollaborationView.as_view(), name='decline_collaboration'),
    
    # Channel Moderation
    path('moderation/', views.ChannelModerationView.as_view(), name='moderation'),
    path('moderation/comments/', views.ChannelCommentModerationView.as_view(), name='comment_moderation'),
    path('moderation/subscribers/', views.SubscriberModerationView.as_view(), name='subscriber_moderation'),
    
    # API Endpoints for HTMX/AJAX
    path('api/check-handle/', views.CheckHandleView.as_view(), name='check_handle'),
    path('api/<str:handle>/toggle-subscribe/', views.ToggleSubscribeView.as_view(), name='toggle_subscribe'),
    path('api/<str:handle>/subscriber-count/', views.SubscriberCountView.as_view(), name='subscriber_count'),
    path('api/channel-suggestions/', views.ChannelSuggestionsView.as_view(), name='channel_suggestions'),
    path('api/trending-channels/', views.TrendingChannelsView.as_view(), name='trending_channels'),
    
    # Featured & Recommendations
    path('featured/', views.FeaturedChannelsView.as_view(), name='featured'),
    path('recommended/', views.RecommendedChannelsView.as_view(), name='recommended'),
    path('trending/', views.TrendingChannelsView.as_view(), name='trending'),
    path('new/', views.NewChannelsView.as_view(), name='new'),
]