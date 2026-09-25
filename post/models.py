from django.db import models

# Create your models here.

from django.contrib.auth import get_user_model
User = get_user_model()

from django.core.exceptions import ValidationError

class Governorate(models.Model):
    name = models.CharField(max_length=15, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to="gallery/governorate", default="gallery/governorate/default.jpg",null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.name}'

class City(models.Model):
    name = models.CharField(max_length=15, unique=True, null=True, blank=True)
    governorate = models.ForeignKey(Governorate, on_delete=models.SET_NULL, null=True, blank=True)
    objects = models.Manager()

    def __str__(self):
        return f'{self.name}'

class PostOffice(models.Model):
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.city.name}'


class Parcel(models.Model):
    from transfer.models import Client
    client_sender = models.ForeignKey(Client, related_name="client_sender_parcels", related_query_name="client_sender_parcels" , on_delete=models.SET_NULL, null=True, blank=True)
    client_receiver = models.ForeignKey(Client, related_name="client_receiver_parcels", related_query_name="client_receiver_parcels", on_delete=models.SET_NULL, null=True, blank=True)
    sender = models.ForeignKey(User, related_name='user_sender_parcels', related_query_name='user_sender_parcels', on_delete=models.SET_NULL, null=True, blank=True)
    receiver = models.ForeignKey(User, related_name='user_receiver_parcels', related_query_name='user_receiver_parcels', on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, related_name="send_employee_parcels", related_query_name="send_employee_parcels", on_delete=models.SET_NULL, null=True, blank=True)
    delivery_employee = models.ForeignKey(User, related_name="delivery_employee_parcels", related_query_name="delivery_employee_parcels", on_delete=models.SET_NULL, null=True, blank=True, )
    parcel_employee = models.ForeignKey(User, related_name="pickup_employee_parcels", related_query_name="pickup_employee_parcels", on_delete=models.SET_NULL, null=True, blank=True)
    sent_mail = models.ForeignKey(PostOffice,related_name='send_mail_parcels', related_query_name='send_mail_parcels', on_delete=models.SET_NULL, null=True, blank=True, )
    inbox_mail = models.ForeignKey(PostOffice, related_name='inbox_mail_parcels', related_query_name='inbox_mail_parcels', on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    postage = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_received = models.BooleanField(default=False)
    received_at = models.DateTimeField(null=True, blank=True)
    in_inbox_mail = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return f'Parcel: {self.id}'

    def clean_client_to_same(self):
        if self.client_sender != None or self.client_receiver != None:
            if self.client_sender == self.client_receiver:
                raise ValidationError(f'client to same')

    def clean_user_to_same(self):
        if self.sender != None or self.receiver != None:
            if self.sender == self.receiver:
                raise ValidationError('user to same')

    def clean_postoffice_to_same(self):
        if self.sent_mail == self.inbox_mail:
            raise ValidationError('postoffice_to_same')

    def clean(self):
        self.clean_client_to_same()
        self.clean_user_to_same()
        self.clean_postoffice_to_same()

class Store(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'Store: {self.id}'

SHOPPING_CHOICES = [
    ('unseen','Unseen'),
    ('seen', 'Seen'),
    ('rejected', 'Rejected'),
    ('resend', 'Resend'),
    ('done', 'Done')
]

class Shopping(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sent_mail = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True)
    inbox_mail = models.ForeignKey(PostOffice, on_delete=models.SET_NULL, null=True, blank=True)
    parcel = models.OneToOneField(Parcel, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    postage = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)
    message = models.CharField(max_length=10, default='unseen', choices=SHOPPING_CHOICES)
    your_price = models.PositiveIntegerField(null=True, blank=True)
    product_price = models.PositiveIntegerField(null=True, blank=True)
    postage_price = models.PositiveIntegerField(null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'Shopping: {self.id}'

    def clean_parcel(self):
        if self.parcel:
            if self.inbox_mail != self.parcel.inbox_mail:
                raise ValidationError('post to other postoffice')
            if self.sent_mail.city.governorate != self.parcel.sent_mail.city.governorate:
                raise ValidationError('post from other governorate')
    def clean(self):
        self.clean_parcel()