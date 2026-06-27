from django.urls import path, include
from .views import (
    UserRegisterationView,
    UserLoginView,
    UserProfileView,
    UserChangePasswordView,
    UserLogoutView,
    UserListView,
    UserDetailsView,
    UserVerificationEmailView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path("register/", UserRegisterationView.as_view(), name="user-registration"),
    path("login/", UserLoginView.as_view(), name="user-login"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path(
        "change-password/",
        UserChangePasswordView.as_view(),
        name="user-change-password",
    ),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
    path("users/", UserListView.as_view(), name="users-list"),
    path("users/<int:pk>/", UserDetailsView.as_view(), name="user-details"),
    path("verify-user/",UserVerificationEmailView.as_view(),name="verify-user"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
