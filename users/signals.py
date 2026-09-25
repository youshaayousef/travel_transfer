from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from statement.models import Balance
from profiles.models import Profile
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender=User)
def handle_insert_update(sender, instance, created, **kwargs):
    if created:
        Balance.objects.create(user=instance)
        Profile.objects.create(user=instance)
    else:
        pass

@receiver(post_save, sender=EmailAddress)
def handle_insert_update(sender, instance, created, **kwargs):
    user = instance.user
    if created:
        user.is_active = False
        user.save()
    else:
        user.is_active = True
        user.save()