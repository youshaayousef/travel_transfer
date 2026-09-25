from django.db import models

# Create your models here.

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()

from django.db.models import Sum  # For aggregation

from post.models import City


class Station(models.Model):
    name = models.CharField(max_length=25, null=True, blank=True, unique=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'{self.name}-{self.city}'


class Bus(models.Model):
    name = models.CharField(max_length=25, null=True, blank=True, unique=True)
    number = models.PositiveIntegerField(null=True, blank=True, unique=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    objects = models.Manager()

    class Meta:
        verbose_name = 'Bus'
        verbose_name_plural = 'Buses'

    def __str__(self):
        return f'{self.name}-{self.number}'


class Seat(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True)
    number = models.CharField(max_length=25, null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'Seat:{self.id}'


class Journey(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True)
    departure_station = models.ForeignKey(Station, related_name="departure_station_journeys", related_query_name="departure_station_journeys", on_delete=models.SET_NULL, null=True, blank=True,
                                          )
    arrival_station = models.ForeignKey(Station, related_name="arrival_station_journeys", related_query_name="arrival_station_journeys", on_delete=models.SET_NULL, null=True, blank=True,
                                        )
    departure_datetime = models.DateTimeField(null=True, blank=True)
    arrival_datetime = models.DateTimeField(null=True, blank=True)
    price = models.PositiveIntegerField(null=True, blank=True)
    petrol = models.PositiveIntegerField(null=True, blank=True)
    driver = models.PositiveIntegerField(null=True, blank=True)
    collector = models.PositiveIntegerField(null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'Journey:{self.id}'

    def clean_datetime(self):
        if self.arrival_datetime <= self.departure_datetime:
            raise ValidationError(f'departure before arrival')

    def clean_journey(self):
        from django.db.models import Q
        conflicting_rows = Journey.objects.exclude(pk=self.pk)

        for row in conflicting_rows:
            if self.bus == row.bus:
                if (self.departure_datetime >= row.departure_datetime
                ) and (
                        self.departure_datetime <= row.arrival_datetime
                ):
                    raise ValidationError("find journey: departure between")
                if (self.arrival_datetime >= row.departure_datetime
                ) and (
                        self.arrival_datetime <= row.arrival_datetime
                ):
                    raise ValidationError("find journey: arrival between")
                if (self.departure_datetime <= row.departure_datetime
                ) and (
                        self.arrival_datetime >= row.arrival_datetime
                ):
                    raise ValidationError("find journey: around")

    def clean(self):
        self.clean_datetime()
        self.clean_journey()


class Schedule(models.Model):
    category = models.CharField(max_length=1, null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True)
    departure_station = models.ForeignKey(Station, related_name="departure_station_schedules", related_query_name="departure_station_schedules", on_delete=models.SET_NULL, null=True, blank=True,
                                          )
    arrival_station = models.ForeignKey(Station, related_name="arrival_station_schedules", related_query_name="arrival_station_schedules", on_delete=models.SET_NULL, null=True, blank=True,
                                        )
    departure_datetime = models.DateTimeField(null=True, blank=True)
    arrival_datetime = models.DateTimeField(null=True, blank=True)
    price = models.PositiveIntegerField(null=True, blank=True)
    petrol = models.PositiveIntegerField(null=True, blank=True)
    driver = models.PositiveIntegerField(null=True, blank=True)
    collector = models.PositiveIntegerField(null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'Schedule:{self.id}'

    def clean_datetime(self):
        if self.arrival_datetime <= self.departure_datetime:
            raise ValidationError(f'departure before arrival')

    def clean_journey(self):
        conflicting_rows = Schedule.objects.exclude(pk=self.pk)

        for row in conflicting_rows:
            if self.bus == row.bus and self.category == row.category:
                if (self.departure_datetime >= row.departure_datetime
                ) and (
                        self.departure_datetime <= row.arrival_datetime
                ):
                    raise ValidationError("find journey: departure between")
                if (self.arrival_datetime >= row.departure_datetime
                ) and (
                        self.arrival_datetime <= row.arrival_datetime
                ):
                    raise ValidationError("find journey: arrival between")
                if (self.departure_datetime <= row.departure_datetime
                ) and (
                        self.arrival_datetime >= row.arrival_datetime
                ):
                    raise ValidationError("find journey: around")

    def clean(self):
        self.clean_datetime()
        self.clean_journey()


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'Reservation: {self.id}'

    @property
    def price(self):
        price = ReservationDetails.objects.filter(
            reservation=self
        ).aggregate(
            price=Sum("journey__price")
        )["price"] or 0
        return price


class ReservationDetails(models.Model):
    journey = models.ForeignKey(Journey, on_delete=models.SET_NULL, null=True, blank=True)
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'ReservationDetail {self.id}'

    def clean_reservation(self):
        conflicting_rows = ReservationDetails.objects.exclude(pk=self.pk).filter(journey=self.journey)

        for row in conflicting_rows:
            if self.seat == row.seat:
                raise ValidationError("booked seat")

    def clean(self):
        self.clean_reservation()
