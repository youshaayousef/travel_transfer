from django.db import models

# Create your models here.
# from django.contrib.auth import get_user_model
# User = get_user_model()
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_blocked = models.BooleanField(default=False)
    is_ATM = models.BooleanField(default=False)
    is_postmaster = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=13, null=True, blank=True, unique=True)
    email = models.EmailField(null=True, blank=True, unique=True)

    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'

    def __str__(self):
        return f'User: {self.id}'