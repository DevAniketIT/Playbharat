from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from accounts.models import Channel

class ChannelListView(ListView):
    model = Channel
    template_name = 'channels/list.html'
    context_object_name = 'channels'
    paginate_by = 24

class ChannelDetailView(DetailView):
    model = Channel
    template_name = 'channels/detail.html'
    context_object_name = 'channel'
    slug_field = 'handle'
    slug_url_kwarg = 'handle'
    
    def get_object(self):
        handle = self.kwargs['handle']
        if not handle.startswith('@'):
            handle = f'@{handle}'
        return get_object_or_404(Channel, handle=handle)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        channel = self.get_object()
        
        # Add recent videos (when Video model is available)
        context['recent_videos'] = []
        
        # Add subscription status for logged-in users
        context['is_subscribed'] = False
        if self.request.user.is_authenticated:
            # This will be implemented when subscription model is available
            context['is_subscribed'] = False
        
        return context

# Placeholder views for now
class ChannelBrowseView(ChannelListView):
    template_name = 'channels/browse.html'

class ChannelSearchView(ChannelListView):
    template_name = 'channels/search.html'

class ChannelCategoriesView(ChannelListView):
    template_name = 'channels/categories.html'

class ChannelCategoryView(ChannelListView):
    template_name = 'channels/category.html'

class ChannelDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/dashboard.html')

class ChannelCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/create.html')

class ChannelEditView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/edit.html')

class ChannelSettingsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/settings.html')

class ChannelAnalyticsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/analytics.html')

class ChannelContentView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/content.html')

class ChannelCommunityView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/community.html')

class ChannelMonetizationView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/monetization.html')

class ChannelVideosView(DetailView):
    model = Channel
    template_name = 'channels/videos.html'
    context_object_name = 'channel'
    
    def get_object(self):
        handle = self.kwargs['handle']
        if not handle.startswith('@'):
            handle = f'@{handle}'
        return get_object_or_404(Channel, handle=handle)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add channel videos to context when Video model is available
        context['videos'] = []
        return context

class ChannelPlaylistsView(DetailView):
    model = Channel
    template_name = 'channels/playlists.html'
    context_object_name = 'channel'
    
    def get_object(self):
        handle = self.kwargs['handle']
        if not handle.startswith('@'):
            handle = f'@{handle}'
        return get_object_or_404(Channel, handle=handle)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add channel playlists to context when Playlist model is available
        context['playlists'] = []
        return context

class ChannelAboutView(DetailView):
    model = Channel
    template_name = 'channels/about.html'
    context_object_name = 'channel'
    
    def get_object(self):
        handle = self.kwargs['handle']
        if not handle.startswith('@'):
            handle = f'@{handle}'
        return get_object_or_404(Channel, handle=handle)

class ChannelCommunityPostsView(DetailView):
    model = Channel
    template_name = 'channels/community_posts.html'
    context_object_name = 'channel'
    
    def get_object(self):
        handle = self.kwargs['handle']
        if not handle.startswith('@'):
            handle = f'@{handle}'
        return get_object_or_404(Channel, handle=handle)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add community posts when available
        context['posts'] = []
        return context

class ChannelSubscribeView(LoginRequiredMixin, View):
    def post(self, request, handle):
        return JsonResponse({'status': 'success'})

class ChannelUnsubscribeView(LoginRequiredMixin, View):
    def post(self, request, handle):
        return JsonResponse({'status': 'success'})

class ChannelFollowView(LoginRequiredMixin, View):
    def post(self, request, handle):
        return JsonResponse({'status': 'success'})

class ChannelReportView(LoginRequiredMixin, View):
    def post(self, request, handle):
        return JsonResponse({'status': 'success'})

class SubscriptionsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/subscriptions.html')

class ManageSubscriptionsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/manage_subscriptions.html')

class SubscriptionFeedView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/subscription_feed.html')

class CollaborationsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/collaborations.html')

class InviteCollaboratorView(LoginRequiredMixin, View):
    def post(self, request):
        return JsonResponse({'status': 'success'})

class AcceptCollaborationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        return JsonResponse({'status': 'success'})

class DeclineCollaborationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        return JsonResponse({'status': 'success'})

class ChannelModerationView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/moderation.html')

class ChannelCommentModerationView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/comment_moderation.html')

class SubscriberModerationView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'channels/subscriber_moderation.html')

class CheckHandleView(View):
    def get(self, request):
        return JsonResponse({'available': True})

class ToggleSubscribeView(LoginRequiredMixin, View):
    def post(self, request, handle):
        return JsonResponse({'status': 'success'})

class SubscriberCountView(View):
    def get(self, request, handle):
        return JsonResponse({'count': 0})

class ChannelSuggestionsView(View):
    def get(self, request):
        return JsonResponse({'channels': []})

class TrendingChannelsView(ChannelListView):
    template_name = 'channels/trending.html'

class FeaturedChannelsView(ChannelListView):
    template_name = 'channels/featured.html'

class RecommendedChannelsView(LoginRequiredMixin, ChannelListView):
    template_name = 'channels/recommended.html'

class NewChannelsView(ChannelListView):
    template_name = 'channels/new.html'