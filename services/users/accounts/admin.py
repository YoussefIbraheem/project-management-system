from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models, transaction
from django.forms.fields import Textarea, TextInput

from accounts.events import UserRegisterEvent
from accounts.publishers import publish_history_event

from .models import User, UserProfile, UserVerification

# Register your models here.


class UserAdmin(BaseUserAdmin):
    search_fields = ["username", "email", "first_name", "last_name"]
    list_filter = ["date_joined", "is_verified"]
    readonly_fields = ["date_joined", "last_login"]
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "date_joined",
        "is_verified",
    ]

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": [
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "usable_password",
                    "password1",
                    "password2",
                ],
            },
        ),
    ]

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "username",
                    "email",
                ]
            },
        ),
        ("Personal Data", {"fields": ["first_name", "last_name"]}),
        ("Advanced Options", {"fields": ["is_verified", "is_superuser"]}),
        ("General Data", {"fields": ["date_joined"]}),
        ("Danger Zone", {"classes": ["collapsable"], "fields": ["password"]}),
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            display_name = ""

            if obj.first_name:
                display_name += obj.first_name

            if obj.last_name:
                display_name += " " + obj.last_name

            UserProfile.objects.create(user=obj)

            event = UserRegisterEvent(
                actor_id=str(request.user.id),
                subject_id=str(obj.id),
                username=obj.username,
                email=obj.email,
                display_name=display_name,
            )
            transaction.on_commit(lambda: publish_history_event(event.to_dict()))


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ["user__username", "user__email"]
    list_filter = ["created_at"]
    list_display = ["user__username", "user__first_name", "user__last_name", "bio"]


class UserVerificationAdmin(admin.ModelAdmin):
    search_fields = ["user__username", "user__email"]
    list_filter = ["created_at"]
    list_display = ["user__username", "user__first_name", "user__last_name", "code"]


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserVerification, UserVerificationAdmin)
