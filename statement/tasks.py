from background_task import background
from datetime import datetime
from django.utils import timezone
from .models import Withdraw, Deposit, Balance

from travel.models import Reservation
from post.models import Shopping, Parcel
from transfer.models import Gift, UndirectTransfer, DirectTransfer

from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum  # For aggregation

def get_last_balance(user, first_day_of_last_month, last_day_of_last_month):
    # Aggregating withdrawals
    withdraws = Withdraw.objects.filter(
        customer=user,
        datetime__gte=first_day_of_last_month,
        datetime__lte=last_day_of_last_month,
    ).aggregate(
        total_withdraws=Sum("amount")
    )["total_withdraws"] or 0

    # Aggregating deposits
    deposits = Deposit.objects.filter(
        customer=user,
        datetime__gte=first_day_of_last_month,
        datetime__lte=last_day_of_last_month,
    ).aggregate(
        total_deposits=Sum("amount")
    )["total_deposits"] or 0

    # Summing reservation costs
    reservations = Reservation.objects.filter(
            user=user,
            created_at__gte=first_day_of_last_month,
            created_at__lte=last_day_of_last_month,
        ).aggregate(
        total_price=Sum("reservationdetails__journey__price")
    )["total_price"] or 0

    # Aggregating transfers received (income)
    income = Gift.objects.filter(
        payee=user,
        created_at__gte=first_day_of_last_month,
        created_at__lte=last_day_of_last_month,
    ).aggregate(
        total_income=Sum("gift")
    )["total_income"] or 0

    income_from_client = UndirectTransfer.objects.filter(
        payee_user=self.user,
        created_at__gte=first_day_of_last_month,
        created_at__lte=last_day_of_last_month,
    ).aggregate(
        total_income_from_client=Sum("amount")
    )["total_income_from_client"] or 0

    # Aggregating transfers sent (expense)
    expense = Gift.objects.filter(
        payer=user,
        created_at__gte=first_day_of_last_month,
        created_at__lte=last_day_of_last_month,
    ).aggregate(
        total_expense=Sum("price")
    )["total_expense"] or 0

    expense_to_client = DirectTransfer.objects.filter(
        payer=self.user,
        created_at__gte=first_day_of_last_month,
        created_at__lte=last_day_of_last_month,
    ).aggregate(
        total_expense_to_client=Sum("price")
    )["total_expense_to_client"] or 0

    # Aggregating parcel postage costs
    parcels = Parcel.objects.filter(
        sender=user,
        created_at__gte=first_day_of_last_month,
        created_at__lte=last_day_of_last_month,
    ).aggregate(
        total_postages=Sum("postage")
    )["total_postages"] or 0

    # Aggregating shopping delivery costs
    shoppings = Shopping.objects.filter(
        receiver=user,
        created_at__gte=first_day_of_last_month,
        created_at__lte=last_day_of_last_month,
    ).aggregate(
        total_postages=Sum("postage")
    )["total_postages"] or 0

    # Calculating total negative and positive balances
    negative = withdraws + reservations + expense + expense_to_client + parcels + shoppings
    positive = deposits + income + income_from_client

    # Returning the net balance
    return positive - negative + Balance.objects.get(user=user).last_balance


@background(schedule=1)
def archive_last_balance():
    today = timezone.now()
    if today.month == 1 and today.day == 1:
        first_day_of_last_year = (today.replace(day=1, month=1) - relativedelta(months=12)).date()
        last_day_of_last_year = (today.replace(day=1, month=1) - relativedelta(days=1)).date()
        for i in Balance.objects.all():
            i.last_balance= get_last_balance(i.user, first_day_of_last_year, last_day_of_last_year)
            i.save()