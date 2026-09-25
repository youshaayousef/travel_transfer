from django.db import models

# Create your models here.
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
User = get_user_model()

MIN_FEE = 1
MAX_FEE = 99999
class Fee(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True, unique=True)
    min = models.PositiveIntegerField(null=True, blank=True)
    max = models.PositiveIntegerField(null=True, blank=True)
    fee = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(MIN_FEE), MaxValueValidator(MAX_FEE)])

    objects = models.Manager()

    def __str__(self):
        return f'Fee: {self.id}'

    def clean_fee(self):
        if self.min >= self.max:
            raise ValidationError(f'min not min!')

    def clean(self):
        self.clean_fee()

class Gift(models.Model):
    payer = models.ForeignKey(User, related_name="payer_gifts", related_query_name="payer_gifts", on_delete=models.SET_NULL, null=True, blank=True)
    payee = models.ForeignKey(User, related_name="payee_gifts", related_query_name="payee_gifts", on_delete=models.SET_NULL, null=True, blank=True)
    gift = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(MIN_FEE), MaxValueValidator(MAX_FEE)])
    price = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    objects = models.Manager()


    def __str__(self):
        return f'Gift: {self.id}'

    @property
    def fee(self):
        return Fee.objects.filter(min__lte=self.gift, max__gt=self.gift).first().fee

    def clean_payee_payer(self):
        if self.payee == self.payer:
            raise ValidationError(f'payee to payee!')

    def clean(self):
        self.clean_payee_payer()

class Client(models.Model):
    firstname = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=100, null=True, blank=True)
    nationality_number = models.CharField(max_length=11, null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return f'{self.phone_number}'

class UndirectTransfer(models.Model):
    delivery_employee = models.ForeignKey(User,related_name="delivery_employee_undirect_transfers", related_query_name="delivery_employee_undirect_transfers", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, related_name="transfer_employee_undirect_transfers", related_query_name="transfer_employee_undirect_transfers", on_delete=models.SET_NULL, null=True, blank=True)
    payee_user = models.ForeignKey(User, related_name="payee_user_undirect_transfers", related_query_name="payee_user_undirect_transfers", on_delete=models.SET_NULL, null=True, blank=True)
    payer = models.ForeignKey(Client, related_name="payer_undirect_transfers", related_query_name="payer_undirect_transfers", on_delete=models.SET_NULL, null=True, blank=True)
    payee = models.ForeignKey(Client, related_name="payee_undirect_transfers", related_query_name="payee_undirect_transfers", on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(MIN_FEE), MaxValueValidator(MAX_FEE)])
    price = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_received = models.BooleanField(default=False)
    received_at = models.DateTimeField(null=True, blank=True)
    from statement.models import ATM
    delivery_atm = models.ForeignKey(ATM, related_name="delivery_atm_undirect_transfers", related_query_name="delivery_atm_undirect_transfers", on_delete=models.SET_NULL, null=True, blank=True)
    transfer_atm = models.ForeignKey(ATM, related_name="transfer_atm_undirect_transfers", related_query_name="transfer_atm_undirect_transfers", on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return f'UndirectTransfer: {self.id}'

    @property
    def fee(self):
        return Fee.objects.filter(min__lte=self.amount, max__gt=self.amount).first().fee

    def clean_delivery_transfer_atm(self):
        if self.delivery_atm == self.transfer_atm:
            raise ValidationError(f'atm to same atm!')

    def clean_payee_payer(self):
        if self.payee == self.payer:
            raise ValidationError('payee to payee!')


    def clean(self):
        self.clean_delivery_transfer_atm()
        self.clean_payee_payer()

class DirectTransfer(models.Model):
    delivery_employee = models.ForeignKey(User, related_name="delivery_employee_direct_transfers", related_query_name="delivery_employee_direct_transfers", on_delete=models.SET_NULL, null=True, blank=True,
                                          )

    payer = models.ForeignKey(User, related_name="payer_direct_transfers", related_query_name="payer_direct_transfers", on_delete=models.SET_NULL, null=True, blank=True)
    payee = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(MIN_FEE), MaxValueValidator(MAX_FEE)])
    price = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_received = models.BooleanField(default=False)
    received_at = models.DateTimeField(null=True, blank=True)
    from statement.models import ATM
    delivery_atm = models.ForeignKey(ATM, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    objects = models.Manager()

    def __str__(self):
        return f'DirectTransfer: {self.id}'

    @property
    def fee(self):
        return Fee.objects.filter(min__lte=self.amount, max__gt=self.amount).first().fee