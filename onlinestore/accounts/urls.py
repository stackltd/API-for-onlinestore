from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api import (
    SignInView,
    SignOutView,
    SignUpView,
    ProfileAPIView,
    ProfileAvatarAPIView,
    ProfilePasswordAPIView,
)

app_name = "accounts"


urlpatterns = [
    path("sign-in/", SignInView.as_view(), name="sign-in"),
    path("sign-out/", SignOutView.as_view(), name="sign-out"),
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("profile/avatar/", ProfileAvatarAPIView.as_view(), name="profile-avatar"),
    path(
        "profile/password/", ProfilePasswordAPIView.as_view(), name="profile-password"
    ),
]
