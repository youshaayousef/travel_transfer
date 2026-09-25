from rest_framework import serializers
from .models import *

from users.serializers import UserSerializer

from django.contrib.auth import get_user_model
User = get_user_model()

class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = '__all__'

class GiftSerializer(serializers.ModelSerializer):
    payer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    payee_detail = serializers.SerializerMethodField()
    payee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    payee_detail = serializers.SerializerMethodField()
    fee = serializers.SerializerMethodField()
    class Meta:
        model = Gift
        fields = '__all__'
        ordering = ['-created_at']
        depth = 1
        extra_kwargs = {
            'gift': {
                'required': True,
                'min_value': 1,
                'max_value': 99999
            },
            'payee': {
                'required': True
            },
        }

    def get_fee(self, obj):
        # return obj.fee or 0
        return getattr(obj, 'fee', 0)


    def get_payer_detail(self, obj):
        return UserSerializer(obj.payer).data if obj.payer else None
    def get_payee_detail(self, obj):
        return UserSerializer(obj.payee).data if obj.payee else None


    def validate(self, data):
        payer = data.get('payer')
        payee = data.get('payee')
        if payee == payer:
            raise serializers.ValidationError({'payee':'payee to payee!'})
        return data

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class UndirectTransferSerializer(serializers.ModelSerializer):
    payee = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False)
    payee_detail = serializers.SerializerMethodField()

    payee_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    payee_user_detail = serializers.SerializerMethodField()

    payer = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False)
    payer_detail = serializers.SerializerMethodField()

    from users.serializers import UserSerializer
    delivery_employee = UserSerializer(required=False)
    user = UserSerializer(required=False)

    from statement.models import ATM
    delivery_atm = serializers.PrimaryKeyRelatedField(queryset=ATM.objects.all(), required=False)
    delivery_atm_detail = serializers.SerializerMethodField()

    transfer_atm = serializers.PrimaryKeyRelatedField(queryset=ATM.objects.all(), required=False)
    transfer_atm_detail = serializers.SerializerMethodField()

    fee = serializers.SerializerMethodField()

    class Meta:
        model = UndirectTransfer
        fields = '__all__'
        depth = 2
        extra_kwargs = {
            'amount': {
                'required': True,
                'min_value': 1,
                'max_value': 99999
            },
            'payer': {
                'required': True,
            }
        }

    def get_payee_detail(self, obj):
        return ClientSerializer(obj.payee).data if obj.payee else None

    def get_payee_user_detail(self, obj):
        return UserSerializer(obj.payee_user).data if obj.payee_user else None

    def get_payer_detail(self, obj):
        return ClientSerializer(obj.payer).data if obj.payer else None

    def get_delivery_atm_detail(self, obj):
        from statement.serializers import ATMSerializer
        return ATMSerializer(obj.delivery_atm).data if obj.delivery_atm else None

    def get_transfer_atm_detail(self, obj):
        from statement.serializers import ATMSerializer
        return ATMSerializer(obj.transfer_atm).data if obj.transfer_atm else None

    def get_fee(self, obj):
        # return obj.fee or 0
        return getattr(obj, 'fee', 0)

    def validate(self, data):
        request = self.context.get('request')
        payee = data.get('payee')
        payer = data.get('payer')
        payee_user = data.get('payee_user')
        delivery_atm = data.get('delivery_atm')
        transfer_atm = data.get('transfer_atm')

        if request.method == 'POST':
            if not payee and not payee_user:
                raise serializers.ValidationError({'payee':'required', 'payee_user':'required'})

        if transfer_atm and delivery_atm and delivery_atm == transfer_atm:
            raise serializers.ValidationError({'transfer_atm':'atm to same atm!'})

        if payee and payer and payee == payer:
            raise serializers.ValidationError({'payee':'payee to payee!'})
        return data


class DirectTransferSerializer(serializers.ModelSerializer):
    payee = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False)
    payee_detail = serializers.SerializerMethodField()

    payer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    payer_detail = serializers.SerializerMethodField()

    from statement.models import ATM
    delivery_atm = serializers.PrimaryKeyRelatedField(queryset=ATM.objects.all(), required=False)
    delivery_atm_detail = serializers.SerializerMethodField()

    fee = serializers.SerializerMethodField()

    from users.serializers import UserSerializer
    delivery_employee = UserSerializer(required=False)

    class Meta:
        model = DirectTransfer
        fields = '__all__'
        depth = 2
        extra_kwargs = {
            'amount': {
                'required': True,
                'min_value': 1,
                'max_value': 99999
            },
            'payee': {
                'required': True,
            }
        }

    def get_payee_detail(self, obj):
        return ClientSerializer(obj.payee).data if obj.payee else None

    def get_payer_detail(self, obj):
        return UserSerializer(obj.payer).data if obj.payer else None

    def get_delivery_atm_detail(self, obj):
        from statement.serializers import ATMSerializer
        return ATMSerializer(obj.delivery_atm).data if obj.delivery_atm else None

    def get_fee(self, obj):
        # return obj.fee or 0
        return getattr(obj, 'fee', 0)
