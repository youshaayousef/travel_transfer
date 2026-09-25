from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Bus, Seat

@receiver(post_save, sender=Bus)
def handle_insert_update(sender, instance, created, **kwargs):
    if created:
        for i in range(instance.capacity):
            Seat.objects.create(number=i+1, bus=instance)
    else:
        pass