import json
from typing import Any
from urllib import response

from django.contrib.auth import authenticate, hashers, password_validation
from psycopg import logger
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from utils.generate_unique_number import generate_verification_code

from .models import User, UserProfile, UserVerification


class UserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(read_only=True, source="profile.bio")

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
            "bio",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]

    def to_representation(self, instance):
        user_has_profile = UserProfile.objects.filter(user=instance).exists()
        if not user_has_profile:
            UserProfile.objects.create(user=instance)

        return super().to_representation(instance)


class UserRegisterationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        write_only=True, min_length=8, max_length=16
    )
    bio = serializers.CharField(read_only=True, source="profile.bio")

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "bio",
            "profile_picture",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
            "password": {"required": True, "write_only": True},
            "password_confirm": {"required": True, "write_only": True},
            "profile_picture": {"required": False},
            "bio": {"required": False},
        }

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

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError("Passwords don't match!")
        password_validation.validate_password(attrs.get("password"))
        attrs["password"] = hashers.make_password(attrs.get("password"))
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create(**validated_data)
        UserProfile.objects.create(user=user)
        if validated_data.get("bio"):
            UserProfile.objects.filter(user=user).update(bio=validated_data["bio"])
        return user


class UserLoginJWTSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["is_superuser"] = user.is_superuser
        token["sub"] = str(user.id)
        # ...

        return token

    def validate(self, attrs):
        user = authenticate(username=attrs.get("email"), password=attrs.get("password"))

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

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user,
        }


class UserLogoutSerializer(serializers.Serializer):
    def validate(self, attrs):
        request = self.context["request"]
        token = request.data.get("refresh_token")
        refresh_token = RefreshToken(token)
        refresh_token.check_blacklist()
        return attrs

    def save(self, **kwargs):
        request = self.context["request"]
        token = request.data.get("refresh_token")
        refresh_token = RefreshToken(token)
        refresh_token.blacklist()

        return


class UserUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)
    profile_picture = serializers.ImageField(required=False)

    def validate(self, attrs):
        user = self.context["request"].user
        if "email" in attrs:
            email = attrs.get("email")
            if email != user.email:
                if User.objects.filter(email=email).exists():
                    raise serializers.ValidationError("Email already exists.")
        if "username" in attrs:
            username = attrs.get("username")
            if username != user.username:
                if User.objects.filter(username=username).exists():
                    raise serializers.ValidationError("Username already exists.")
        return attrs

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("username", instance.username)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.profile_picture = validated_data.get(
            "profile_picture", instance.last_name
        )
        instance.save()
        if hasattr(instance, "profile"):
            instance.profile.bio = validated_data.get("bio", instance.profile.bio)
            instance.profile.save()
        return instance


class UserDeleteSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs.get("password")):
            raise serializers.ValidationError("Incorrect password.")
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.delete()
        return


class UserPasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):

        user = self.context["request"].user
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError("Incorrect Current Password!")

        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError(
                "Password Confirmation Failed. Make sure to enter the same new password in both fields"
            )

        password_validation.validate_password(attrs["new_password"])

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        new_password = self.validated_data.get("new_password")
        user.set_password(new_password)
        user.save()
        return user
