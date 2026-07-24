from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    UserChangePasswordView,
    UserDeleteView,
    UserDetailsView,
    UserListView,
    UserLoginView,
    UserLogoutView,
    UserRegisterationView,
    UserUpdateView,
    UserVerificationEmailView,
    UserView,
)

urlpatterns = [
    path("register/", UserRegisterationView.as_view(), name="user-registration"),
    path("login/", UserLoginView.as_view(), name="user-login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("update/", UserUpdateView.as_view(), name="user-update"),
    path("profile/", UserView.as_view(), name="user-profile"),
    path("delete/", UserDeleteView.as_view(), name="user-delete"),
    path(
        "change-password/",
        UserChangePasswordView.as_view(),
        name="user-change-password",
    ),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
    path("users/", UserListView.as_view(), name="users-list"),
    path("users/<int:pk>/", UserDetailsView.as_view(), name="user-details"),
    path("verify-user/", UserVerificationEmailView.as_view(), name="verify-user"),
    path(
        "password-reset/",
        include("django_rest_passwordreset.urls"),
        name="password-reset",
    ),
]
