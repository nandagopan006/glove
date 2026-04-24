from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.http import HttpResponseForbidden

def admin_required(view_func):
   
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Access denied. Administrative privileges required.")
                return redirect('home')
        
        messages.error(request, "Please sign in to access the admin panel.")
        return redirect('admin_signin')
    return _wrapped_view

def unauthenticated_user(view_func):
   
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def user_required(view_func):
 
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('admin_dashboard')
        
        messages.error(request, "Please sign in to continue.")
        return redirect('signin')
    return _wrapped_view
