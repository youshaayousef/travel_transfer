from rest_framework import serializers

from .models import *

class NotificationSerializer(serializers.ModelSerializer):
    from users.serializers import UserSerializer
    user = UserSerializer()
    class Meta:
        model = Notification
        fields = '__all__'
        depth = 1