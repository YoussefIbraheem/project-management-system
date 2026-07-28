import tempfile
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .. import serializers, views


class BaseAPITestCase(TestCase):
    """
    Common setup: an API client, and mocks around every outbound side effect
    so tests never depend on (or fail because of) an external broker,
    notifications service or SMTP server.

    Patching is per-module by design. `views` and `serializers` each import
    `publish_history_event` into their own namespace, so patching only one of
    them leaves the other publishing to the real broker.
    """

    def setUp(self):
        super().setUp()
        self._media_tmpdir = tempfile.TemporaryDirectory()
        self._media_override = override_settings(MEDIA_ROOT=self._media_tmpdir.name)
        self._media_override.enable()
        self.addCleanup(self._media_override.disable)
        self.addCleanup(self._media_tmpdir.cleanup)
        self.client = APIClient()

        history_patcher = patch.object(views, "publish_history_event")
        notification_patcher = patch.object(views, "publish_notification_event")
        self.mock_publish_history_event = history_patcher.start()
        self.mock_publish_notification_event = notification_patcher.start()
        self.addCleanup(history_patcher.stop)
        self.addCleanup(notification_patcher.stop)

        # `_send_otp_code` lives in serializers and reaches the broker on
        # registration and on login-while-unverified.
        serializer_history_patcher = patch.object(
            serializers, "publish_history_event"
        )
        self.mock_serializer_publish_history_event = serializer_history_patcher.start()
        self.addCleanup(serializer_history_patcher.stop)

        # `.delay` would queue a real Celery task against the live broker.
        otp_email_patcher = patch.object(serializers.send_verification_email, "delay")
        self.mock_send_verification_email = otp_email_patcher.start()
        self.addCleanup(otp_email_patcher.stop)
