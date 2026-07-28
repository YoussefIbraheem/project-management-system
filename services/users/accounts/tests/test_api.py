import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_rest_passwordreset.models import ResetPasswordToken
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .. import views
from ..mailers import password_reset as password_reset_mailer
from ..models import User, UserProfile, UserVerification
from .base import BaseAPITestCase

logger = logging.getLogger(__name__)


class UserRegistrationTestCase(BaseAPITestCase):
    """Test cases for the user registration endpoint."""

    def setUp(self):
        super().setUp()
        self.register_url = reverse("user-registration")
        self.valid_payload = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.valid_payload["email"]).exists())

    def test_user_registration_does_not_leak_password(self):
        response = self.client.post(self.register_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)

    def test_user_registration_publishes_history_and_notification_events(self):
        response = self.client.post(self.register_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.mock_publish_history_event.assert_called_once()
        self.mock_publish_notification_event.assert_called_once()

    def test_user_registration_creates_profile(self):
        response = self.client.post(self.register_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.valid_payload["email"])
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_user_registration_password_hashed(self):
        response = self.client.post(self.register_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.valid_payload["email"])
        self.assertNotEqual(user.password, self.valid_payload["password"])
        self.assertTrue(user.check_password(self.valid_payload["password"]))

    def test_user_registration_passwords_mismatch(self):
        data = {**self.valid_payload, "password_confirm": "DifferentPassword123"}
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=data["email"]).exists())

    def test_user_registration_weak_password(self):
        data = {**self.valid_payload, "password": "weak", "password_confirm": "weak"}
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=data["email"]).exists())

    def test_user_registration_password_confirm_too_short(self):
        data = {**self.valid_payload, "password_confirm": "sh0rt"}
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_password_confirm_too_long(self):
        long_password = "ThisPasswordIsWayTooLong123"
        data = {
            **self.valid_payload,
            "password": long_password,
            "password_confirm": long_password,
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        User.objects.create_user(
            email="testuser@example.com",
            username="existing",
            password="TestPassword123",
        )
        response = self.client.post(self.register_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_username(self):
        User.objects.create_user(
            email="existing@example.com",
            username="testuser",
            password="TestPassword123",
        )
        response = self.client.post(self.register_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_email_format(self):
        data = {**self.valid_payload, "email": "not-an-email"}
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_required_fields(self):
        data = {"email": "testuser@example.com", "username": "testuser"}
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_optional_names_still_succeeds(self):
        """first_name / last_name aren't marked required, so omitting them
        should still succeed."""
        data = {
            "email": "noname@example.com",
            "username": "noname",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UserLoginTestCase(BaseAPITestCase):
    """Test cases for the user login endpoint."""

    def setUp(self):
        super().setUp()
        self.login_url = reverse("token-obtain-pair")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="TestPassword123",
        )
        self.user.is_verified = True
        self.user.save()
        UserProfile.objects.create(user=self.user)

    def test_user_login_success(self):
        data = {"email": "testuser@example.com", "password": "TestPassword123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("refresh", response.data["tokens"])
        self.assertIn("access", response.data["tokens"])
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_user_login_publishes_history_event(self):
        data = {"email": "testuser@example.com", "password": "TestPassword123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.mock_publish_history_event.assert_called_once()
        # Login should not trigger a notifications event.
        self.mock_publish_notification_event.assert_not_called()

    def test_user_login_access_token_has_custom_claims(self):
        data = {"email": "testuser@example.com", "password": "TestPassword123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        access_token = AccessToken(response.data["tokens"]["access"])
        self.assertEqual(access_token["sub"], str(self.user.id))
        self.assertEqual(access_token["is_superuser"], self.user.is_superuser)

    def test_user_login_superuser_claim_true_for_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="AdminPass123"
        )
        admin.is_verified = True
        admin.save()

        data = {"email": "admin@example.com", "password": "AdminPass123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        access_token = AccessToken(response.data["tokens"]["access"])
        self.assertTrue(access_token["is_superuser"])

    def test_user_login_invalid_credentials(self):
        data = {"email": "testuser@example.com", "password": "WrongPassword"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_unverified_user(self):
        unverified_user = User.objects.create_user(
            email="unverified@example.com",
            username="unverified",
            password="TestPassword123",
        )
        unverified_user.is_verified = False
        unverified_user.save()

        data = {"email": "unverified@example.com", "password": "TestPassword123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Account not verified. A new verification code has been sent to your email.",
            response.data["non_field_errors"][0],
        )

    def test_user_login_unverified_user_creates_verification_code(self):
        unverified_user = User.objects.create_user(
            email="unverified@example.com",
            username="unverified",
            password="TestPassword123",
        )
        unverified_user.is_verified = False
        unverified_user.save()

        data = {"email": "unverified@example.com", "password": "TestPassword123"}
        self.client.post(self.login_url, data)

        self.assertTrue(UserVerification.objects.filter(user=unverified_user).exists())

    def test_user_login_inactive_user(self):
        inactive_user = User.objects.create_user(
            email="inactive@example.com",
            username="inactive",
            password="TestPassword123",
        )
        inactive_user.is_verified = True
        inactive_user.is_active = False
        inactive_user.save()

        data = {"email": "inactive@example.com", "password": "TestPassword123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_nonexistent_email(self):
        data = {"email": "nonexistent@example.com", "password": "TestPassword123"}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_missing_email(self):
        response = self.client.post(self.login_url, {"password": "TestPassword123"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_missing_password(self):
        response = self.client.post(self.login_url, {"email": "testuser@example.com"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTestCase(BaseAPITestCase):
    """Test cases for the (read-only) user profile endpoint."""

    def setUp(self):
        super().setUp()
        self.profile_url = reverse("user-profile")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="TestPassword123",
            first_name="Test",
            last_name="User",
        )
        self.user.is_verified = True
        self.user.save()
        self.profile = UserProfile.objects.create(user=self.user, bio="Original bio")

    def test_get_user_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["bio"], "Original bio")

    def test_get_user_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_profile_auto_creates_missing_profile(self):
        new_user = User.objects.create_user(
            email="newuser@example.com",
            username="newuser",
            password="TestPassword123",
        )
        self.client.force_authenticate(user=new_user)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())

    def test_profile_endpoint_does_not_support_put(self):
        """UserProfileView only defines `get`, so PUT should be rejected."""
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.profile_url, {"bio": "Nope"})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class UserUpdateTestCase(BaseAPITestCase):
    """
    Test cases for the user update endpoint (PUT).
    """

    def setUp(self):
        super().setUp()
        self.update_url = reverse("user-update")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="TestPassword123",
            first_name="Test",
            last_name="User",
        )
        self.user.is_verified = True
        self.user.save()
        # A profile is required up-front for most tests in this class: see
        # the class docstring for why.
        self.profile = UserProfile.objects.create(user=self.user, bio="Original bio")

    def test_update_succeeds_even_when_profile_does_not_exist_yet(self):
        user_without_profile = User.objects.create_user(
            email="noprofile@example.com",
            username="noprofile",
            password="TestPassword123",
            is_verified=True,
        )
        user_without_profile.save()
        client = APIClient()
        client.force_authenticate(user=user_without_profile)
        response = client.put(self.update_url, {"first_name": "New"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_names_and_username_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "username": "updateduser",
        }
        response = self.client.put(self.update_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")
        self.assertEqual(self.user.username, "updateduser")

    def test_update_email_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.update_url, {"email": "new@example.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@example.com")

    def test_update_with_unchanged_email_does_not_conflict(self):
        """Submitting the user's own current email should not be treated as
        a duplicate."""
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.update_url, {"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_with_unchanged_username_does_not_conflict(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.update_url, {"username": self.user.username})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_duplicate_email_rejected(self):
        User.objects.create_user(
            email="taken@example.com", username="other", password="TestPassword123"
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.update_url, {"email": "taken@example.com"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, "taken@example.com")

    def test_update_duplicate_username_rejected(self):
        User.objects.create_user(
            email="other@example.com", username="taken", password="TestPassword123"
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.update_url, {"username": "taken"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_bio_persists_on_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.update_url, {"bio": "New bio"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "New bio")

    def test_update_profile_picture_success(self):
        self.client.force_authenticate(user=self.user)
        image = SimpleUploadedFile(
            "avatar.gif",
            b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00"
            b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
            content_type="image/gif",
        )
        response = self.client.put(
            self.update_url, {"profile_picture": image}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_partial_single_field(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.update_url, {"first_name": "OnlyThis"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "OnlyThis")
        self.assertEqual(self.user.last_name, "User")

    def test_update_empty_payload_succeeds(self):
        """All fields are optional, so an empty payload is technically
        valid and should just leave the user unchanged."""
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.update_url, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_unauthenticated(self):
        response = self.client.put(self.update_url, {"first_name": "Nope"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDeleteTestCase(BaseAPITestCase):
    """
    Test cases for the user delete endpoint.
    """

    def setUp(self):
        super().setUp()

        self.client = APIClient()
        self.delete_url = reverse("user-delete")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="TestPassword123",
        )
        self.user.is_verified = True
        self.user.save()

    def test_delete_unauthenticated(self):
        response = self.client.delete(self.delete_url, {"password": "TestPassword123"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_delete_success_with_correct_password(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_url, {"password": "TestPassword123"})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_delete_incorrect_password_rejected(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_url, {"password": "WrongPassword"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())


class UserChangePasswordTestCase(BaseAPITestCase):
    """Test cases for the change password endpoint."""

    def setUp(self):
        super().setUp()
        self.change_password_url = reverse("user-change-password")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="OldPassword123",
        )
        self.user.is_verified = True
        self.user.save()

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "OldPassword123",
            "new_password": "NewPassword123",
            "confirm_new_password": "NewPassword123",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123"))

    def test_change_password_publishes_history_event(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "OldPassword123",
            "new_password": "NewPassword123",
            "confirm_new_password": "NewPassword123",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_publish_history_event.assert_called_once()

    def test_change_password_incorrect_current(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "WrongPassword",
            "new_password": "NewPassword123",
            "confirm_new_password": "NewPassword123",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OldPassword123"))

    def test_change_password_mismatch(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "OldPassword123",
            "new_password": "NewPassword123",
            "confirm_new_password": "DifferentPassword123",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_weak_password(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "current_password": "OldPassword123",
            "new_password": "weak",
            "confirm_new_password": "weak",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        data = {
            "current_password": "OldPassword123",
            "new_password": "NewPassword123",
            "confirm_new_password": "NewPassword123",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_missing_fields(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.change_password_url, {"current_password": "OldPassword123"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutTestCase(BaseAPITestCase):
    """
    Test cases for the logout endpoint.
    """

    def setUp(self):
        super().setUp()
        self.logout_url = reverse("user-logout")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="TestPassword123",
        )
        self.user.is_verified = True
        self.user.save()
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_logout_success_with_refresh_token_in_body(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.logout_url, {"refresh_token": self.refresh_token}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_success_with_empty_body(self):
        """Since the serializer has no required fields, an empty body is
        currently accepted too."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.logout_url, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated(self):
        response = self.client.post(
            self.logout_url, {"refresh_token": self.refresh_token}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_the_provided_refresh_token(self):
        """
        Ensure that the provided refresh token is blacklisted after a successful logout.
        """
        self.client.force_authenticate(user=self.user)
        self.client.post(self.logout_url, {"refresh_token": self.refresh_token})

        refresh_response = self.client.post(
            reverse("token-refresh"), {"refresh": self.refresh_token}
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserListTestCase(BaseAPITestCase):
    """Test cases for the (admin-only) user list endpoint."""

    def setUp(self):
        super().setUp()
        self.list_url = reverse("users-list")

        self.admin = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="AdminPass123"
        )
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            username="user1",
            password="TestPassword123",
            is_verified=True,
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            username="user2",
            password="TestPassword123",
            is_verified=False,
        )

    def test_list_users_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_list_users_as_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_unauthenticated(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_filter_by_email(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url, {"email": "user1@example.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], "user1@example.com")

    def test_list_users_filter_by_username(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url, {"username": "user1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["username"], "user1")

    def test_list_users_filter_by_verification_status(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url, {"is_verified": True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data:
            self.assertTrue(user["is_verified"])

    def test_list_users_filter_by_nonexistent_email_returns_empty(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url, {"email": "nobody@example.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class UserDetailsTestCase(BaseAPITestCase):
    """Test cases for the (admin-only) single user detail endpoint."""

    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="AdminPass123"
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            username="user",
            password="TestPassword123",
            is_verified=True,
        )
        self.details_url = reverse("user-details", args=[self.user.id])

    def test_get_user_details_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.details_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["username"], self.user.username)

    def test_get_user_details_as_non_admin_forbidden(self):
        other_user = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="TestPassword123",
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.details_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_details_unauthenticated(self):
        response = self.client.get(self.details_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_details_nonexistent_user(self):
        self.client.force_authenticate(user=self.admin)
        nonexistent_url = reverse("user-details", args=[999999])
        response = self.client.get(nonexistent_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_details_response_structure(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.details_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        required_fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_verified",
            "date_joined",
            "last_login",
        ]
        for field in required_fields:
            self.assertIn(field, response.data)


class UserVerificationEmailTestCase(BaseAPITestCase):
    """
    Test cases for the email verification endpoint.
    """

    def setUp(self):
        super().setUp()
        self.verify_url = reverse("verify-user")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="TestPassword123",
        )
        self.user.is_verified = False
        self.user.save()
        self.verification = UserVerification.objects.create(
            user=self.user, code="123456"
        )

    def test_verify_email_success(self):
        response = self.client.post(
            self.verify_url, {"email": self.user.email, "code": "123456"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        self.assertFalse(
            UserVerification.objects.filter(pk=self.verification.pk).exists()
        )

    def test_verify_email_success_publishes_history_event(self):
        response = self.client.post(
            self.verify_url, {"email": self.user.email, "code": "123456"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_publish_history_event.assert_called_once()

    def test_verify_email_wrong_code(self):
        response = self.client.post(
            self.verify_url, {"email": self.user.email, "code": "000000"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)

    def test_verify_email_nonexistent_user(self):
        response = self.client.post(
            self.verify_url, {"email": "nobody@example.com", "code": "123456"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_missing_email(self):
        response = self.client.post(self.verify_url, {"code": "123456"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_missing_code(self):
        response = self.client.post(self.verify_url, {"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_does_not_require_authentication(self):
        response = self.client.post(
            self.verify_url, {"email": self.user.email, "code": "wrong"}
        )

        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_email_invalid_code_returns_clear_message(self):
        response = self.client.post(
            self.verify_url, {"email": self.user.email, "code": "000000"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "Invalid verification code.")

    def test_verify_email_expired_code_requests_new_code(self):
        expired_verification = UserVerification.objects.get(pk=self.verification.pk)
        expired_verification.created_at = datetime.now(timezone.utc) - timedelta(
            hours=2
        )
        expired_verification.save(update_fields=["created_at"])

        with patch.object(views, "_send_otp_code", return_value=True) as mock_send_otp:
            response = self.client.post(
                self.verify_url, {"email": self.user.email, "code": "123456"}
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("A new code has been sent", response.data)
        mock_send_otp.assert_called_once_with(self.user)


class PasswordResetTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.reset_request_url = reverse("password_reset:reset-password-request")
        self.user = User.objects.create_user(
            email="resetuser@example.com",
            username="resetuser",
            password="TestPassword123",
        )
        self.user.is_verified = True
        self.user.save()

    def test_password_reset_request_creates_token_and_queues_email(self):
        with patch.object(
            password_reset_mailer._dispatch_password_reset_email, "delay"
        ) as mock_delay:
            response = self.client.post(
                self.reset_request_url, {"email": self.user.email}
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": "OK"})
        token = ResetPasswordToken.objects.get(user=self.user)
        mock_delay.assert_called_once()
        user_id, reset_url = mock_delay.call_args.args
        self.assertEqual(user_id, self.user.id)
        self.assertIn(token.key, reset_url)
        self.assertIn("/api/v1/password-reset/confirm/", reset_url)

    def test_password_reset_request_for_unknown_email_returns_ok_without_token(self):
        with patch.object(
            password_reset_mailer._dispatch_password_reset_email, "delay"
        ) as mock_delay:
            response = self.client.post(
                self.reset_request_url, {"email": "missing@example.com"}
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": "OK"})
        self.assertFalse(ResetPasswordToken.objects.exists())
        mock_delay.assert_not_called()
