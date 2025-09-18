from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def superuser_required(function=None, redirect_field_name=None):
    """
    Decorator for views that checks that the logged in user is a superuser,
    redirects to the login page if necessary.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'You need to be logged in to access this area.')
                return redirect('accounts:login')
            
            if not request.user.is_superuser:
                messages.error(request, 'You do not have permission to access the admin area.')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator


def admin_required(view_func):
    """
    Decorator that requires user to be a superuser or staff member
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You need to be logged in to access this area.')
            return redirect('accounts:login')
        
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'You do not have permission to access the admin area.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view