from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Parcel

@receiver(post_save, sender=Parcel)
def handle_insert_update(sender, instance, created, **kwargs):
    from notifications.models import Notification
    if created:
        if instance.receiver:
            Notification.objects.create(user=instance.receiver, parcel=instance)
    else:
        pass