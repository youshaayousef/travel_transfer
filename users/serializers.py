from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework import serializers
from statement.models import Balance
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number',
                  'first_name', 'last_name', 'is_blocked',
                  'is_ATM', 'is_postmaster',
                  'is_superuser', 'is_staff',
                  'date_joined', 'last_login', 'balance']

        extra_kwargs = {
            'password': {
                'write_only':True
            },
        }

    def get_balance(self, obj):
        return obj.balance.balance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number', 'first_name', 'last_name']

    def create(self, validated_data):
        # Use the `create_user` method to ensure the password is hashed
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


from django.contrib.auth import update_session_auth_hash
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect old password.")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

from auth_kit.serializers import RegisterSerializer

class CustomRegisterSerializer(RegisterSerializer):
    def save(self, **kwargs):
        request = self.context.get("request")
        user = super().save(request=request)
        user.is_active = False
        user.save()
        return user

