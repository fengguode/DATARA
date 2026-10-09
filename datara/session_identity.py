"""Minimal same-origin session views; identity is always Django's request.user.

WP05/TK64; CUS10; SR20-SR21/SR73. Public registration and API tokens are out
of scope. Django stores only its normal password hash and server-side session.
"""
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.views.decorators.cache import never_cache


@never_cache
def home(request):
    """Small non-dashboard landing page for the local login redirect."""
    if not request.user.is_authenticated:
        return auth_views.redirect_to_login(request.get_full_path())
    return render(request, "datara/home.html", {"username": request.user.get_username()})


class LocalLoginView(auth_views.LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class LocalLogoutView(auth_views.LogoutView):
    # Django 5.2 LogoutView accepts POST only and retains CSRF middleware.
    next_page = "login"

