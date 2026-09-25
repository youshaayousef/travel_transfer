from rest_framework import serializers

from .models import *

class ProfileSerializer(serializers.ModelSerializer):
    from users.serializers import UserSerializer
    user = UserSerializer(required=False)
    class Meta:
        model = Profile
        fields = '__all__'