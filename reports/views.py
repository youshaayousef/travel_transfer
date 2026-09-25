from django.shortcuts import render

# Create your views here.

from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Sum, Count, F

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from django.utils import timezone
from datetime import datetime

from .serializers import *
from statement.models import Withdraw, Deposit
from post.models import Shopping
from travel.models import Reservation
from post.models import Shopping, Parcel
from transfer.models import Gift, UndirectTransfer, DirectTransfer

class MonthlyPieReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        year = request.query_params.get("year", None)
        month = request.query_params.get("month", None)
        if not year or not month:
            return Response({"detail": "Year, Month parameters are required"}, status=HTTP_400_BAD_REQUEST)

        withdraw_data = Withdraw.objects.filter(
            datetime__year=year,
            datetime__month=month,
            customer=user,
        ).annotate(
            year=ExtractYear("datetime"),
            month=ExtractMonth("datetime")
        ).values("year", "month").annotate(
            total_withdraw=Sum("amount")
        ).order_by("year", "month")

        deposit_data = Deposit.objects.filter(
            datetime__year=year,
            datetime__month=month,
            customer=user,
        ).annotate(
            year=ExtractYear("datetime"),
            month=ExtractMonth("datetime")
        ).values("year", "month").annotate(
            total_deposit=Sum("amount")
        ).order_by("year", "month")

        reservation_data = Reservation.objects.filter(
            created_at__year=year,
            created_at__month=month,
            user=user,
        ).annotate(
            year=ExtractYear("created_at"),
            month=ExtractMonth("created_at"),
        ).values("year", "month").annotate(
            total_reservation=Sum("reservationdetails__journey__price")
        )

        income_data = Gift.objects.filter(
            created_at__year=year,
            created_at__month=month,
            payee=user,
            is_paid=True,
        ).annotate(
            year=ExtractYear("created_at"),
            month=ExtractMonth("created_at"),
        ).values("year", "month").annotate(
            total_income=Sum("gift")
        )

        income_data = income_data.union(
            Gift.objects.filter(
                created_at__year=year,
                created_at__month=month,
                payee=user,
                is_paid=False,
            ).annotate(
                year=ExtractYear("created_at"),
                month=ExtractMonth("created_at"),
            ).values("year", "month").annotate(
                total_income=2*Sum("gift")-Sum('price')
            )
        )


        income_from_client_data = UndirectTransfer.objects.filter(
            created_at__year=year,
            created_at__month=month,
            payee_user=user,
            is_paid=True,
        ).annotate(
            year=ExtractYear("created_at"),
            month=ExtractMonth("created_at"),
        ).values("year", "month").annotate(
            total_income_from_client=Sum("amount")
        )

        income_from_client_data = income_from_client_data.union(
            UndirectTransfer.objects.filter(
                created_at__year=year,
                created_at__month=month,
                payee_user=user,
                is_paid=False,
            ).annotate(
                year=ExtractYear("created_at"),
                month=ExtractMonth("created_at"),
            ).values("year", "month").annotate(
                total_income_from_client=2*Sum("amount")-Sum("price")
            )
        )

        expense_data = Gift.objects.filter(
            created_at__year=year,
            created_at__month=month,
            payer=user,
            is_paid=True,
        ).annotate(
            year=ExtractYear("created_at"),
            month=ExtractMonth("created_at"),
        ).values("year", "month").annotate(
            total_expense=Sum("price")
        )

        expense_data = expense_data.union(
            Gift.objects.filter(
                created_at__year=year,
                created_at__month=month,
                payer=user,
                is_paid=False,
            ).annotate(
                year=ExtractYear("created_at"),
                month=ExtractMonth("created_at"),
            ).values("year", "month").annotate(
                total_expense=Sum("gift")
            )
        )

        expense_to_client_data = DirectTransfer.objects.filter(
            created_at__year=year,
            created_at__month=month,
            payer=user,
            is_paid=True,
        ).annotate(
            year=ExtractYear("created_at"),
            month=ExtractMonth("created_at"),
        ).values("year", "month").annotate(
            total_expense_to_client=Sum("price")
        )

        expense_to_client_data = expense_to_client_data.union(
            DirectTransfer.objects.filter(
                created_at__year=year,
                created_at__month=month,
                payer=user,
                is_paid=False,
            ).annotate(
                year=ExtractYear("created_at"),
                month=ExtractMonth("created_at"),
            ).values("year", "month").annotate(
                total_expense_to_client=Sum("amount")
            )
        )

        parcels_data = Parcel.objects.filter(
            created_at__year=year,
            created_at__month=month,
            sender=user,
            is_paid=True,
        ).annotate(
            year=ExtractYear("created_at"),
            month=ExtractMonth("created_at"),
        ).values("year", "month").annotate(
            total_parcels=Sum("postage")
        )

        parcels_data = parcels_data.union(
            Parcel.objects.filter(
                created_at__year=year,
                created_at__month=month,
                receiver=user,
                is_paid=False,
            ).annotate(
                year=ExtractYear("created_at"),
                month=ExtractMonth("created_at"),
            ).values("year", "month").annotate(
                total_parcels=Sum("postage")
            )
        )


        shoppings_data = Shopping.objects.filter(
            created_at__year=year,
            created_at__month=month,
            receiver=user,
        ).annotate(
            year=ExtractYear("created_at"),
            month=ExtractMonth("created_at"),
        ).values("year", "month").annotate(
            total_shoppings=Sum("postage")
        )

        # Merge the results into a single report dictionary
        report = {}
        for entry in withdraw_data:
            key = f"{entry['year']}/{str(entry['month']).zfill(2)}"
            report[key] = {
                "month": key,
                "total_withdraw": entry["total_withdraw"],
                "total_deposit": 0,
                "total_reservation": 0,
                "total_income": 0,
                "total_income_from_client": 0,
                "total_expense": 0,
                "total_expense_to_client": 0,
                "total_parcels": 0,
                "total_shoppings": 0,
            }

        for entry in deposit_data:
            key = f"{entry['year']}/{str(entry['month']).zfill(2)}"
            if key in report:
                report[key]["total_deposit"] = entry["total_deposit"]
            else:
                report[key] = {
                    "month": key,
                    "total_withdraw": 0,
                    "total_deposit": entry["total_deposit"],
                    "total_reservation": 0,
                    "total_income": 0,
                    "total_income_from_client": 0,
                    "total_expense": 0,
                    "total_expense_to_client": 0,
                    "total_parcels": 0,
                    "total_shoppings": 0,
                }

        for entry in reservation_data:
            key = f"{entry['year']}/{str(entry['month']).zfill(2)}"
            if key in report:
                report[key]["total_reservation"] = entry["total_reservation"]
            else:
                report[key] = {
                    "month": key,
                    "total_withdraw": 0,
                    "total_deposit": 0,
                    "total_reservation": entry["total_reservation"],
                    "total_income": 0,
                    "total_income_from_client": 0,
                    "total_expense": 0,
                    "total_expense_to_client": 0,
                    "total_parcels": 0,
                    "total_shoppings": 0,
                }

        for entry in income_data:
            key = f"{entry['year']}/{str(entry['month']).zfill(2)}"
            if key in report:
                report[key]["total_income"] += entry["total_income"]
            else:
                report[key] = {
                    "month": key,
                    "total_withdraw": 0,
                    "total_deposit": 0,
                    "total_reservation": 0,
                    "total_income": entry["total_income"],
                    "total_income_from_client": 0,
                    "total_expense": 0,
                    "total_expense_to_client": 0,
                    "total_parcels": 0,
                    "total_shoppings": 0,
                }

        for entry in income_from_client_data:
            key = f"{entry['year']}/{str(entry['month']).zfill(2)}"
            if key in report:
                report[key]["total_income_from_client"] += entry["total_income_from_client"]
            else:
                report[key] = {
                    "month": key,
                    "total_withdraw": 0,
                    "total_deposit": 0,
                    "total_reservation": 0,
                    "total_income": 0,
                    "total_income_from_client": entry["total_income_from_client"],
                    "total_expense": 0,
                    "total_expense_to_client": 0,
                    "total_parcels": 0,
                    "total_shoppings": 0,
                }

        for entry in expense_data:
            key = f"{entry['year']}/{str(entry['month']).zfill(2)}"
            if key in report:
                report[key]["total_expense"] += entry["total_expense"]
            else:
                report[key] = {
                    "month": key,
                    "total_withdraw": 0,
                    "total_deposit": 0,
                    "total_reservation": 0,
                    "total_income": 0,
                    "total_income_from_client": 0,
                    "total_expense": entry["total_expense"],
                    "total_expense_to_client": 0,
                    "total_parcels": 0,
                    "total_shoppings": 0,
                }

        for entry in expense_to_client_data:
            key = f"{entry['year']}/{str(entry['month']).zfill(2)}"
            if key in report:
                report[key]["total_expense_to_client"] += entry["total_expense_to_client"]
            else:
                report[key] = {
                    "month": key,
                    "total_withdraw": 0,
                    "total_deposit": 0,
                    "total_reservation": 0,
                    "total_income": 0,
                    "total_income_from_client": 0,
                    "total_expense": 0,
                    "total_expense_to_client": entry["total_expense_to_client"],
                    "total_parcels": 0,
                    "total_shoppings": 0,
                }

        for entry in parcels_data:
            key = f"{entry['year']}/{str(entry['month']).zfill(2)}"
            if key in report:
                report[key]["total_parcels"] += entry["total_parcels"]
            else:
                report[key] = {
                    "month": key,
                    "total_withdraw": 0,
                    "total_deposit": 0,
                    "total_reservation": 0,
                    "total_income": 0,
                    "total_income_from_client": 0,
                    "total_expense": 0,
                    "total_expense_to_client": 0,
                    "total_parcels": entry["total_parcels"],
                    "total_shoppings": 0,
                }

        for entry in shoppings_data:
            key = f"{entry['year']}/{str(entry['month']).zfill(2)}"
            if key in report:
                report[key]["total_shoppings"] = entry["total_shoppings"]
            else:
                report[key] = {
                    "month": key,
                    "total_withdraw": 0,
                    "total_deposit": 0,
                    "total_reservation": 0,
                    "total_income": 0,
                    "total_income_from_client": 0,
                    "total_expense": 0,
                    "total_expense_to_client": 0,
                    "total_parcels": 0,
                    "total_shoppings": entry["total_shoppings"]
                }
        return Response(list(report.values()))


class YearlyBarReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.query_params.get("year", None)  # Year for monthly aggregation

        if not year:
            return Response({"detail": "Year is required"}, status=HTTP_400_BAD_REQUEST)

        # Aggregate data monthly for the given year
        monthly_report = Deposit.objects.filter(
            customer=user,
            datetime__year=year,
        ).annotate(
            month=ExtractMonth("datetime")
        ).values("month").annotate(
            total_amount=Sum("amount")
        ).order_by("month")
        # Transform data for response
        report_data = [
            {"month": {item['month']}, "total_amount": item["total_amount"]}
            for item in monthly_report
        ]

        return Response(report_data)


class JourneyReservationCount(ListAPIView):
    today = timezone.now()
    queryset = (Reservation.objects.filter(
        reservationdetails__journey__departure_datetime__lte=today
    ).annotate(
        journey=F("reservationdetails__journey__id")
    ).values("journey").annotate(
        total_count=Count("id")
    )).order_by("-journey")
    serializer_class = JourneyReservationCountSerializer
    #ordering_fields = ['-journey']
    permission_classes = [IsAdminUser]
    from index.paginations import CustomPagination
    pagination_class = CustomPagination

from rest_framework.generics import RetrieveAPIView
class JourneyRetrieve(RetrieveAPIView):
    from travel.models import Journey
    queryset = Journey.objects.filter(departure_datetime__lte=timezone.now())
    from travel.serializers import JourneySerializer
    serializer_class = JourneySerializer
    lookup_field = "id"
    permission_classes = [IsAdminUser]
    filterset_fields = ['departure_station__city__governorate', 'arrival_station__city__governorate']
    ordering_fields = ['departure_datetime']