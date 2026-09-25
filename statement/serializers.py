from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework import serializers

from users.serializers import UserSerializer
from .models import *

class ATMSerializer(serializers.ModelSerializer):
    from post.models import City
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False)
    city_detail = serializers.SerializerMethodField()
    class Meta:
        model = ATM
        fields = '__all__'
        depth = 2

    def get_city_detail(self, obj):
        from post.serializers import CitySerializer
        if isinstance(obj, ATM):
            return CitySerializer(obj.city).data if obj.city else None
        return None

class BalanceSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()
    class Meta:
        model = Balance
        fields = ['id', 'user', 'balance']

    def get_balance(self, obj):
        return obj.balance or 0

class DepositSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    customer_detail = serializers.SerializerMethodField()
    from users.serializers import UserSerializer
    user = UserSerializer(required=False)
    class Meta:
        model = Deposit
        fields = '__all__'
        ordering = ["-datetime"]
        depth = 1
        extra_kwargs = {
            'amount': {
                'required': True
            },
            'customer': {
                'required': True
            },
        }

    def get_customer_detail(self, obj):
        return UserSerializer(obj.customer).data if obj.customer else None

class WithdrawSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    customer_detail = serializers.SerializerMethodField()
    from users.serializers import UserSerializer
    user = UserSerializer(required=False)
    class Meta:
        model = Withdraw
        fields = '__all__'
        depth = 1
        extra_kwargs = {
            'amount': {
                'required': True
            },
            'customer': {
                'required': True
            },
        }

    def get_customer_detail(self, obj):
        return UserSerializer(obj.customer).data if obj.customer else None