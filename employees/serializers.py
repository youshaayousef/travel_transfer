from rest_framework import serializers
from .models import *

class EmployeeSerializer(serializers.ModelSerializer):
    from users.serializers import UserSerializer
    user = UserSerializer()
    class Meta:
        model = Employee
        fields = '__all__'