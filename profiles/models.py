from django.db import models

# Create your models here.

from django.contrib.auth import get_user_model
User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default="avatars/default.png")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, null=True, blank=True)
    facebook_account = models.URLField(blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.user.username}\'s Profile'