from django.db import models
from django.contrib.auth.models import AbstractUser

class SmartUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, default="user")
    otp_secret = models.CharField(max_length=6, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
