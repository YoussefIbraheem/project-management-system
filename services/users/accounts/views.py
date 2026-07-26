import logging
from datetime import datetime, timedelta, timezone

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import (
    generics,
    permissions,
    response,
    status,
    views,
)

from .events import (
    UserEmailChangeEvent,
    UserLoginEvent,
    UserLogoutEvent,
    UserPasswordChangeEvent,
    UserRegisterEvent,
)
from .models import User, UserProfile, UserVerification
from .publishers import publish_history_event, publish_notification_event
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserDeleteSerializer,
    UserLogoutSerializer,
    UserPasswordChangeSerializer,
    UserRegisterationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    _send_otp_code,
)

logger = logging.getLogger(__name__)


class UserRegisterationView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @swagger_auto_schema(request_body=UserRegisterationSerializer)
    def post(self, request):
        serializer = UserRegisterationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            actor_id = request.user.id if request.user.id else user.id
            display_name = ""

            if user.first_name:
                display_name += user.first_name

            if user.last_name:
                display_name += " " + user.last_name

            event = UserRegisterEvent(
                actor_id=str(actor_id),
                subject_id=str(user.id),
                username=user.username,
                email=user.email,
                display_name=display_name,
            )
            publish_history_event(event.to_dict())
            publish_notification_event(event.to_dict())

            return response.Response(
                {
                    "message": "User registered successfully. Verification email sent.",
                },
                status=status.HTTP_201_CREATED,
            )
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @swagger_auto_schema(request_body=CustomTokenObtainPairSerializer)
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = data["user"]

            actor_id = request.user.id if request.user.id else user.id

            event = UserLoginEvent(
                actor_id=str(actor_id),
                subject_id=str(user.id),
                username=user.username,
                email=user.email,
            )
            publish_history_event(event.to_dict())

            return response.Response(
                {
                    "message": "User logged in successfully",
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(data["refresh"]),
                        "access": str(data["access"]),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return response.Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class UserView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: UserSerializer()})
    def get(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user).data
            return response.Response(serializer)

        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=request.user)
            serializer = UserSerializer(request.user).data
            return response.Response(serializer)


class UserUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserUpdateSerializer, responses={200: UserSerializer()}
    )
    def put(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()
        return response.Response(serializer.data)

        # return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserDeleteSerializer, responses={204: "User Deleted Successfully!"}
    )
    def delete(self, request):
        serializer = UserDeleteSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserPasswordChangeSerializer,
        responses={
            200: "Password Updated Successfully!",
        },
    )
    def post(self, request):
        serializer = UserPasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()

            actor_id = request.user.id if request.user.id else user.id

            event = UserPasswordChangeEvent(
                actor_id=str(actor_id),
                subject_id=str(user.id),
                change_source="user_request",
                auth_method="password",
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT"),
                sessions_invalidated=True,
            )

            publish_history_event(event.to_dict())

            return response.Response(
                {"message": "Password Updated Successfully!"},
                status=status.HTTP_200_OK,
            )
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserLogoutSerializer,
        responses={200: "User logged out successfully."},
    )
    def post(self, request):
        serializer = UserLogoutSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()

            request_user = request.user

            event = UserLogoutEvent(
                actor_id=str(request_user.id),
                subject_id=str(request_user.id),
                email=request_user.email,
                username=request_user.username,
            )

            publish_history_event(event.to_dict())

            return response.Response(
                {"message": "User logged out successfully."},
                status=status.HTTP_200_OK,
            )
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticated]
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["email", "username", "is_verified"]

    @swagger_auto_schema(serializer_class=UserSerializer(many=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserDetailsView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticated]
    serializer_class = UserSerializer

    @swagger_auto_schema(serializer_class=UserSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserVerificationEmailView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        manual_parameters=[],
        responses={200: "User verified successfully."},
    )
    def post(self, request):

        email = request.data.get("email")
        code = request.data.get("code")

        try:
            user = User.objects.filter(email=email).first()
            if not user:
                return response.Response(
                    "Email not found",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            verification = UserVerification.objects.filter(user=user).last()

            if not verification or verification.created_at < datetime.now(
                timezone.utc
            ) - timedelta(hours=1):
                _send_otp_code(user)
                return response.Response(
                    "Verification code not found or expired. A new code has been sent.",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if verification.code == code:
                logger.info(f"Verifying user {user.email}...")
                user.is_verified = True
                user.save()
                verification.delete()

                actor_id = request.user.id if request.user.id else user.id

                event = UserEmailChangeEvent(
                    actor_id=str(actor_id),
                    subject_id=str(user.id),
                    new_email=user.email,
                )

                publish_history_event(event.to_dict())

                return response.Response("User verified successfully.")
            else:
                return response.Response(
                    "Invalid verification code.",
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return response.Response(
                f"Error Verifying User:{e}", status=status.HTTP_400_BAD_REQUEST
            )
