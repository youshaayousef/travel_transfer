from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Gift, UndirectTransfer


@receiver(post_save, sender=Gift)
def handle_insert_update(sender, instance, created, **kwargs):
    from notifications.models import Notification
    if created:
        Notification.objects.create(user=instance.payee, gift=instance)
    else:
        pass

@receiver(post_save, sender=UndirectTransfer)
def handle_insert_update(sender, instance, created, **kwargs):
    from notifications.models import Notification
    if created:
        if instance.payee_user:
            Notification.objects.create(user=instance.payee_user, undirect_transfer=instance)
    else:
        pass

