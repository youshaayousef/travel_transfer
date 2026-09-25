from django.shortcuts import render

# Create your views here.

from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_201_CREATED
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from .models import *
from statement.models import Balance
from .serializers import *
from index.paginations import CustomPagination
class StationViewSet(ReadOnlyModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['city', 'city__governorate']
    from .paginations import StationsPagination
    pagination_class = StationsPagination

class BusViewSet(ReadOnlyModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    permission_classes = [IsAdminUser]

class SeatViewSet(ReadOnlyModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['bus']
    from .paginations import SeatPagination
    pagination_class = SeatPagination


class JourneyViewSet(ModelViewSet):
    queryset = Journey.objects.filter(departure_datetime__gte=timezone.now())
    serializer_class = JourneySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filterset_fields = ['departure_station', 'arrival_station']
    ordering_fields = ['departure_datetime']

    def create(self, request, *args, **kwargs):
        data = request.data
        if "category" in data and request.user.is_superuser:
            schedule = Schedule.objects.filter(category__exact=data["category"])
            count = schedule.count()
            today = timezone.now()
            day = today.day
            month = today.month
            year = today.year
            from dateutil.relativedelta import relativedelta
            with transaction.atomic():
                counter=0
                for i in schedule:
                    departure_datetime = i.departure_datetime.replace(day=day,month=month,year=year) + relativedelta(days=7)

                    arrival_datetime = i.arrival_datetime.replace(day=day,month=month,year=year) + relativedelta(days=7)

                    Journey.objects.create(
                        bus=i.bus,
                        departure_station=i.departure_station,
                        arrival_station=i.arrival_station,
                        departure_datetime= departure_datetime,
                        arrival_datetime= arrival_datetime,
                        price=i.price,
                        petrol=i.petrol,
                        driver=i.driver,
                        collector=i.collector
                    )
                    counter += 1
            if count == counter:
                return Response({"done":"created"}, status=HTTP_201_CREATED)
        return Response({"detail":"bug"}, status=HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)


class ScheduleViewSet(ModelViewSet):
    queryset = Schedule.objects.filter()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['departure_station', 'arrival_station']
    ordering_fields = ['departure_datetime']

class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    #filterset_fields = ['user']
    ordering = ["-id"]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def get_object(self):
        return get_object_or_404(Reservation, user=self.request.user, id=self.kwargs.get("pk"))

    def create(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        today = timezone.now()
        user = request.user
        with transaction.atomic():
            reservation = self.get_object()
            temp = reservation.reservationdetails_set.all()
            time_delete = temp.first().journey.departure_datetime
            if time_delete - today < timedelta(hours=1):
                return Response({"detail": "can't before 1 hour"}, status=HTTP_400_BAD_REQUEST)
            temp.delete()
            super().destroy(request, *args, **kwargs)
            return Response(status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class ReservationDetailsViewSet(ModelViewSet):
    queryset = ReservationDetails.objects.all()
    serializer_class = ReservationDetailsSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['journey', 'user', 'reservation']

    def get_queryset(self):
        return ReservationDetails.objects.filter(user=self.request.user)

    def get_object(self):
        return get_object_or_404(ReservationDetails, user=self.request.user, id=self.kwargs.get("pk"))

    def create(self, request):
        user = request.user
        data = request.data

        serializer = self.get_serializer(data=data, many=True)
        if serializer.is_valid():
            with transaction.atomic():
                reservation = Reservation.objects.create(user=user)
                journey = get_object_or_404(Journey,id=int(data[0].get("journey")))
                balance = user.balance.balance
                if balance < journey.price * len(data):
                    return Response({"detail": "balance not enough"}, status=HTTP_400_BAD_REQUEST)
                serializer.save(user=user, reservation=reservation)
                return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)
