from rest_framework import serializers

class JourneyReservationCountSerializer(serializers.Serializer):
    journey = serializers.IntegerField()
    total_count = serializers.IntegerField()