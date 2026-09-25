from django.db import models

# Create your models here.

from django.contrib.auth import get_user_model
User = get_user_model()

from django.core.exceptions import ValidationError

class Employee(models.Model):
    from statement.models import ATM
    from post.models import PostOffice
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    atm = models.ForeignKey(ATM, related_name='employees', related_query_name='employees', on_delete=models.CASCADE, null=True, blank=True)
    post_office = models.ForeignKey(PostOffice, related_name='employees', related_query_name='employees', on_delete=models.SET_NULL, null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.user.username}'

    def clean_employee(self):
        if self.atm and self.post_office:
            if self.atm.city != self.post_office.city:
                raise ValidationError('two city!')


    def clean(self):
        self.clean_employee()