from django.db import models

# Create your models here.

from dateutil.relativedelta import relativedelta
from django.db.models import Sum  # For aggregation

from django.contrib.auth import get_user_model
User = get_user_model()

class ATM(models.Model):
    from post.models import City
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.city.name}'

class Deposit(models.Model):
    amount = models.PositiveIntegerField(null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(User, related_name="customer_deposits", related_query_name="customer_deposits", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, related_name="deposit_employee_deposits", related_query_name="deposit_employee_deposits", on_delete=models.SET_NULL, null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'Deposit: {self.id}'

class Withdraw(models.Model):
    amount = models.PositiveIntegerField(null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(User, related_name="customer_withdraws", related_query_name="customer_withdraws", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, related_name="withdraw_employee_withdraws", related_query_name="withdraw_employee_withdraws", on_delete=models.SET_NULL, null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'Withdraw: {self.id}'


class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    last_balance = models.IntegerField(default=0, null=True, blank=True)
    objects = models.Manager()

    def __str__(self):
        return f'Balance: {self.id}'

    @property
    def balance(self):
        from travel.models import Reservation
        from post.models import Shopping, Parcel
        from transfer.models import Gift, UndirectTransfer, DirectTransfer
        from django.utils import timezone
        today = timezone.now()
        first_day_of_year = today.replace(day=1, month=1)
        # Aggregating withdrawals
        withdraws = Withdraw.objects.filter(
            customer=self.user,
            datetime__range=[first_day_of_year, today],
        ).aggregate(
            total_withdraws=Sum("amount")
        )["total_withdraws"] or 0

        # Aggregating deposits
        deposits = Deposit.objects.filter(
            customer=self.user,
            datetime__gte = first_day_of_year,
            datetime__lte = today,
        ).aggregate(
            total_deposits=Sum("amount")
        )["total_deposits"] or 0

        # Summing reservation costs
        reservations = Reservation.objects.filter(
            user=self.user,
            created_at__gte=first_day_of_year,
            created_at__lte=today,
        ).aggregate(
            total_price=Sum("reservationdetails__journey__price")
        )["total_price"] or 0


        income = (Gift.objects.filter(
            payee=self.user,
            created_at__gte=first_day_of_year,
            created_at__lte=today,
            is_paid=True,
        ).aggregate(
            total_income=Sum("gift")
        )["total_income"] or 0)+(
            Gift.objects.filter(
                payee=self.user,
                created_at__gte=first_day_of_year,
                created_at__lte=today,
                is_paid=False,
            ).aggregate(
                total_income=2*Sum("gift")-Sum('price')
            )["total_income"] or 0
        )

        income_from_client = (UndirectTransfer.objects.filter(
            payee_user=self.user,
            created_at__gte=first_day_of_year,
            created_at__lte=today,
            is_paid=True,
        ).aggregate(
            total_income_from_client=Sum("amount")
        )["total_income_from_client"] or 0)+(
            UndirectTransfer.objects.filter(
            payee_user=self.user,
            created_at__gte=first_day_of_year,
            created_at__lte=today,
            is_paid=False,
        ).aggregate(
            total_income_from_client=2*Sum("amount")-Sum("price")
        )["total_income_from_client"] or 0)

        expense = (Gift.objects.filter(
            payer=self.user,
            created_at__gte=first_day_of_year,
            created_at__lte=today,
            is_paid=True,
        ).aggregate(
            total_expense=Sum("price")
        )["total_expense"] or 0)+(
            Gift.objects.filter(
                payer=self.user,
                created_at__gte=first_day_of_year,
                created_at__lte=today,
                is_paid=False,
            ).aggregate(
                total_expense=Sum('gift')
            )["total_expense"] or 0
        )

        expense_to_client = (DirectTransfer.objects.filter(
            payer=self.user,
            created_at__gte=first_day_of_year,
            created_at__lte=today,
            is_paid=True,
        ).aggregate(
            total_expense_to_client=Sum("price")
        )["total_expense_to_client"] or 0)+(
                DirectTransfer.objects.filter(
                    payer=self.user,
                    created_at__gte=first_day_of_year,
                    created_at__lte=today,
                    is_paid=False,
                ).aggregate(
                    total_expense_to_client=Sum("amount")
                )["total_expense_to_client"] or 0
        )

        # Aggregating parcel postage costs
        parcels = (Parcel.objects.filter(
            sender=self.user,
            is_paid=True,
            created_at__gte=first_day_of_year,
            created_at__lte=today,
        ).aggregate(
            total_postages=Sum("postage")
        )["total_postages"] or 0 ) + (
                Parcel.objects.filter(
                    receiver=self.user,
                    is_paid=False,
                    created_at__gte=first_day_of_year,
                    created_at__lte=today,
                ).aggregate(
                    total_postages=Sum("postage")
                )["total_postages"] or 0
        )

        # Aggregating shopping delivery costs
        shoppings = Shopping.objects.filter(
            receiver=self.user,
            created_at__gte=first_day_of_year,
            created_at__lte=today,
        ).aggregate(
            total_postages=Sum("postage")
        )["total_postages"] or 0

        # Calculating total negative and positive balances
        negative = withdraws + reservations + expense + expense_to_client + parcels + shoppings
        positive = deposits + income + income_from_client
        # Returning the net balance
        return positive - negative + self.last_balance