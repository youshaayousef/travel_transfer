from rest_framework import serializers
from .models import *

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'
        depth = 2

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = '__all__'

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = '__all__'

class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = '__all__'
        depth = 3
        ordering = ['departure_datetime']


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'
        depth = 3
        ordering = ['departure_datetime']

class ReservationSerializer(serializers.ModelSerializer):
    from users.serializers import UserSerializer
    user = UserSerializer(required=False)
    price = serializers.SerializerMethodField()
    class Meta:
        model = Reservation
        fields = '__all__'
        ordering = ['-created_at']

    def get_price(self, obj):
        return obj.price or 0


class ReservationDetailsSerializer(serializers.ModelSerializer):
    from users.serializers import UserSerializer
    user = UserSerializer(required=False)
    journey = serializers.PrimaryKeyRelatedField(queryset=Journey.objects.all())
    seat = serializers.PrimaryKeyRelatedField(queryset=Seat.objects.all())
    journey_detail = serializers.SerializerMethodField()
    seat_detail = serializers.SerializerMethodField()
    class Meta:
        model = ReservationDetails
        fields = '__all__'
        depth = 1
    def get_journey_detail(self, obj):
        return JourneySerializer(obj.journey).data if obj.journey else None
    def get_seat_detail(self, obj):
        return SeatSerializer(obj.seat).data if obj.seat else None

    def validate(self, attrs):
        journey = attrs.get("journey")
        seat = attrs.get("seat")
        conflicting_rows = ReservationDetails.objects.filter(journey=journey)

        for row in conflicting_rows:
            if seat == row.seat:
                raise ValidationError({"detail":"booked seat"})

        return attrs