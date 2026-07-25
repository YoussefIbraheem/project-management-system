from dirtyfields import DirtyFieldsMixin
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to="user", blank=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        full_name = super().get_full_name()
        return full_name if full_name.strip() else self.email


class UserProfile(models.Model,DirtyFieldsMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add

    class Meta:
        verbose_name = "User Profile"

    def __str__(self):
        return self.user.email
    

class UserVerification(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="verification")
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)