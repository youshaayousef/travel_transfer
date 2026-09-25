from django.db import models

# Create your models here.

from django.contrib.auth import get_user_model
User = get_user_model()

from travel.models import Reservation
from post.models import Shopping, Parcel, City
from transfer.models import Gift, UndirectTransfer, DirectTransfer

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    gift = models.OneToOneField(Gift, on_delete=models.CASCADE, null=True, blank=True)
    undirect_transfer = models.OneToOneField(UndirectTransfer, on_delete=models.CASCADE, null=True, blank=True)
    parcel = models.OneToOneField(Parcel, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return f'Notification: {self.id}'