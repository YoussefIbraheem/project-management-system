from types import SimpleNamespace
from unittest.mock import patch

from django.template import TemplateDoesNotExist
from django.test import TestCase, override_settings

from .. import mailers as mailers_pkg
from ..mailers import password_reset as password_reset_mailer
from ..mailers import verification as verification_mailer
from ..models import User


class PasswordResetMailerTestCase(TestCase):
    """Unit tests for the password-reset mailer.

    These exercise mailer functions directly, so unlike the API tests they
    need no APIClient, no media root and no publisher patching.
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            email="resetuser@example.com",
            username="resetuser",
            password="TestPassword123",
        )
        self.user.is_verified = True
        self.user.save()

    def test_send_password_reset_email_queues_task_with_confirmation_url(self):
        instance = SimpleNamespace(
            request=SimpleNamespace(
                build_absolute_uri=lambda path: f"https://api.example{path}"
            )
        )
        reset_password_token = SimpleNamespace(user=self.user, key="abc123")

        with patch.object(
            password_reset_mailer._dispatch_password_reset_email, "delay"
        ) as mock_delay:
            password_reset_mailer.send_password_reset_email(
                sender=object(),
                instance=instance,
                reset_password_token=reset_password_token,
            )

        mock_delay.assert_called_once_with(
            self.user.id,
            "https://api.example/api/v1/password-reset/confirm/?token=abc123",
        )

    def test_dispatch_password_reset_email_builds_context_and_sends(self):
        reset_url = "https://api.example/api/v1/password-reset/confirm/?token=abc123"

        with (
            override_settings(APP_NAME="Users Service", SITE_URL="https://example.com"),
            patch.object(
                password_reset_mailer, "send_email", return_value=True
            ) as mock_send_email,
        ):
            password_reset_mailer._dispatch_password_reset_email(
                self.user.id, reset_url
            )

        mock_send_email.assert_called_once()
        template, context, email, subject = mock_send_email.call_args.args
        self.assertEqual(template, password_reset_mailer._PASSWORD_RESET_TEMPLATE)
        self.assertEqual(email, self.user.email)
        self.assertEqual(subject, "Password Reset")
        self.assertEqual(context["user"].id, self.user.id)
        self.assertEqual(context["app_name"], "Users Service")
        self.assertEqual(context["site_url"], "https://example.com")
        self.assertEqual(context["reset_url"], reset_url)


class VerificationMailerTestCase(TestCase):
    def test_build_verification_url_returns_empty_when_not_configured(self):
        user = SimpleNamespace(id=1, email="user@example.com")

        with patch.object(verification_mailer.logger, "warning") as mock_warning:
            url = verification_mailer._build_verification_url(user, "123456")

        self.assertEqual(url, "")
        mock_warning.assert_called_once()

    def test_build_verification_url_includes_email_and_code(self):
        user = SimpleNamespace(id=1, email="user@example.com")

        with override_settings(
            FRONTEND_VERIFICATION_URL="https://frontend.example/verify"
        ):
            url = verification_mailer._build_verification_url(user, "123456")

        self.assertEqual(
            url,
            "https://frontend.example/verify?email=user@example.com&code=123456",
        )

    def test_send_email_renders_and_sends_message(self):
        message = patch("accounts.mailers.EmailMultiAlternatives")
        mock_email_class = message.start()
        self.addCleanup(message.stop)
        email_message = mock_email_class.return_value

        with patch.object(
            mailers_pkg, "render_to_string", return_value="<p>Hello <b>there</b></p>"
        ) as mock_render:
            result = mailers_pkg.send_email(
                "email_templates/user_verification.html",
                {"user": "dummy"},
                "user@example.com",
                "User Verification",
            )

        self.assertTrue(result)
        mock_render.assert_called_once_with(
            "email_templates/user_verification.html", {"user": "dummy"}
        )
        mock_email_class.assert_called_once_with(
            subject="User Verification",
            to=["user@example.com"],
            body="Hello there",
        )
        email_message.attach_alternative.assert_called_once_with(
            "<p>Hello <b>there</b></p>", "text/html"
        )
        email_message.send.assert_called_once_with(fail_silently=False)

    def test_send_email_returns_false_when_template_missing(self):
        with (
            patch.object(
                mailers_pkg,
                "render_to_string",
                side_effect=TemplateDoesNotExist("missing"),
            ),
            patch.object(mailers_pkg.logger, "exception") as mock_exception,
        ):
            result = mailers_pkg.send_email(
                "missing.html", {}, "user@example.com", "User Verification"
            )

        self.assertFalse(result)
        mock_exception.assert_called_once()

    def test_send_verification_email_builds_context_and_sends(self):
        user = User.objects.create_user(
            email="taskuser@example.com",
            username="taskuser",
            password="TestPassword123",
        )

        with (
            override_settings(
                FRONTEND_VERIFICATION_URL="https://frontend.example/verify",
                APP_NAME="Users Service",
                SITE_URL="https://example.com",
            ),
            patch.object(
                verification_mailer, "send_email", return_value=True
            ) as mock_send_email,
            patch.object(verification_mailer.task_logger, "info") as mock_info,
        ):
            result = verification_mailer.send_verification_email(user.id, "999999")

        self.assertTrue(result)
        mock_info.assert_called_once_with(
            "Sending verification email to %s", user.email
        )
        mock_send_email.assert_called_once()
        template, context, email, subject = mock_send_email.call_args.args
        self.assertEqual(template, verification_mailer._VERIFICATION_TEMPLATE)
        self.assertEqual(email, user.email)
        self.assertEqual(subject, "User Verification")
        self.assertEqual(context["user"].id, user.id)
        self.assertEqual(context["verification_code"], "999999")
        self.assertEqual(
            context["verification_url"],
            "https://frontend.example/verify?email=taskuser@example.com&code=999999",
        )
        self.assertEqual(context["app_name"], "Users Service")
        self.assertEqual(context["site_url"], "https://example.com")

    def test_send_verification_email_returns_false_for_missing_user(self):
        with patch.object(
            verification_mailer.User.objects, "get", side_effect=User.DoesNotExist
        ):
            result = verification_mailer.send_verification_email(999, "123456")

        self.assertFalse(result)
