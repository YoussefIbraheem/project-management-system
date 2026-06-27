import json
from typing import Any
from urllib import response

from django.contrib.auth import authenticate, hashers, password_validation
from psycopg import logger
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from utils.generate_unique_number import generate_verification_code

from .models import User, UserProfile, UserVerification


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["is_superuser"] = user.is_superuser
        token["sub"] = str(user.id)
        # ...

        return token


class UserRegisterationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        write_only=True, min_length=8, max_length=16
    )

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
            "password": {"required": True, "write_only": True},
            "password_confirm": {"required": True, "write_only": True},
        }

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create(**validated_data)
        UserProfile.objects.create(user=user)
        return user

    def validate_username(self, value):
        value_exists = User.objects.filter(username=value).exists()

        if value_exists:
            raise serializers.ValidationError(
                "A user with this username already exists!"
            )

        return value

    def validate_email(self, value):
        value_exists = User.objects.filter(email=value).exists()

        if value_exists:
            raise serializers.ValidationError("A user with this email already exists!")

        return value

    def validate(self, data):
        if data.get("password") != data.get("password_confirm"):
            raise serializers.ValidationError("Passwords don't match!")
        password_validation.validate_password(data.get("password"))
        data["password"] = hashers.make_password(data.get("password"))
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_verified",
            "date_joined",
            "last_login",
            "profile_picture",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get("email"), password=data.get("password"))

        if not user:
            raise serializers.ValidationError("Invalid Credentials.")

        if not user.is_verified:
            code = UserVerification.objects.update_or_create(
                user=user, defaults={"code": generate_verification_code()}
            )[0]

            logger.info(f"USER DATA:{user.id} \n CODE:{code.code}")

            raise serializers.ValidationError(
                "Account not verified. A new verification code has been sent to your email."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive, refer to us for reverification."
            )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    date_joined = serializers.DateTimeField(source="user.date_joined", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["email", "username", "first_name", "last_name", "date_joined", "bio"]


class UserPasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect Current Password!")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError(
                "Password Confirmation Failed. Make sure to enter the same new password in both fields"
            )

        password_validation.validate_password(attrs["new_password"])

        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class UserLogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True, write_only=True)

    def validate_refresh_token(self, value):
        try:
            token = RefreshToken(value)
        except Exception as e:
            raise serializers.ValidationError("Invalid refresh token") from e
        return value

    def save(self):
        token = RefreshToken(self.validated_data["refresh_token"])
        token.blacklist()

        return
