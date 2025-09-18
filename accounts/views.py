from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Channel
from .forms import UserRegistrationForm, ChannelCreationForm, UserProfileForm

User = get_user_model()

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        return render(request, 'accounts/register.html', {'form': form})

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        from django import forms
        
        class LoginForm(forms.Form):
            username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username or Email'
            }))
            password = forms.CharField(widget=forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }))
        
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})
    
    def post(self, request):
        from django import forms
        
        class LoginForm(forms.Form):
            username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username or Email'
            }))
            password = forms.CharField(widget=forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }))
        
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password')
        return render(request, 'accounts/login.html', {'form': form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Logged out successfully!')
        return redirect('home')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        try:
            context['channel'] = self.request.user.channel
        except:
            context['channel'] = None
        return context

class PublicProfileView(TemplateView):
    template_name = 'accounts/public_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = kwargs.get('username')
        context['profile_user'] = get_object_or_404(User, username=username)
        return context

class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserProfileForm(instance=request.user)
        return render(request, 'accounts/edit_profile.html', {'form': form})
    
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        return render(request, 'accounts/edit_profile.html', {'form': form})

class CreateChannelView(LoginRequiredMixin, View):
    def get(self, request):
        # Check if user already has a channel
        if hasattr(request.user, 'channel'):
            messages.info(request, 'You already have a channel')
            return redirect('accounts:channel_dashboard')
        
        form = ChannelCreationForm()
        return render(request, 'accounts/create_channel.html', {'form': form})
    
    def post(self, request):
        if hasattr(request.user, 'channel'):
            messages.error(request, 'You already have a channel')
            return redirect('accounts:channel_dashboard')
        
        form = ChannelCreationForm(request.POST, request.FILES)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.user = request.user
            channel.save()
            messages.success(request, 'Channel created successfully!')
            return redirect('accounts:channel_dashboard')
        return render(request, 'accounts/create_channel.html', {'form': form})

class EditChannelView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            channel = request.user.channel
        except Channel.DoesNotExist:
            messages.error(request, 'You need to create a channel first')
            return redirect('accounts:create_channel')
        
        form = ChannelCreationForm(instance=channel)
        return render(request, 'accounts/edit_channel.html', {'form': form, 'channel': channel})
    
    def post(self, request):
        try:
            channel = request.user.channel
        except Channel.DoesNotExist:
            messages.error(request, 'You need to create a channel first')
            return redirect('accounts:create_channel')
        
        form = ChannelCreationForm(request.POST, request.FILES, instance=channel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Channel updated successfully!')
            return redirect('accounts:channel_dashboard')
        return render(request, 'accounts/edit_channel.html', {'form': form, 'channel': channel})

class ChannelDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/channel_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['channel'] = self.request.user.channel
        except Channel.DoesNotExist:
            context['channel'] = None
        return context

class AccountSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/settings.html'

class PrivacySettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/privacy_settings.html'

class NotificationSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/notification_settings.html'