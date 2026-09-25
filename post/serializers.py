from rest_framework import serializers
from .models import *

from users.serializers import UserSerializer
from transfer.serializers import ClientSerializer

class GovernorateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Governorate
        fields = '__all__'
        ordering = 'name'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'
        ordering = 'name'
        depth = 1

class PostOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostOffice
        fields = '__all__'
        depth = 2

class ParcelSerializer(serializers.ModelSerializer):
    from transfer.models import Client
    client_sender = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False)
    client_sender_detail = serializers.SerializerMethodField()

    client_receiver = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False)
    client_receiver_detail = serializers.SerializerMethodField()

    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    sender_detail = serializers.SerializerMethodField()

    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    receiver_detail = serializers.SerializerMethodField()

    sent_mail = serializers.PrimaryKeyRelatedField(queryset=PostOffice.objects.all(), required=False)
    sent_mail_detail = serializers.SerializerMethodField()

    inbox_mail = serializers.PrimaryKeyRelatedField(queryset=PostOffice.objects.all(), required=False)
    inbox_mail_detail = serializers.SerializerMethodField()

    from users.serializers import UserSerializer
    user = UserSerializer(required=False)
    delivery_employee = UserSerializer(required=False)
    parcel_employee = UserSerializer(required=False)

    class Meta:
        model = Parcel
        fields = '__all__'
        depth = 3
        extra_kwargs = {
            'postage' : {
                'required': True
            },
            'inbox_mail': {
                'required': True
            },
            'details': {
                'required': True
            }
        }

    def get_client_sender_detail(self, obj):
        if(isinstance(obj, Parcel)):
            return ClientSerializer(obj.client_sender).data
        return None

        # return ClientSerializer(obj.client_sender).data if obj.client_sender else None

    def get_sender_detail(self, obj):
        if (isinstance(obj, Parcel)):
            return UserSerializer(obj.sender).data
        return None

    def get_client_receiver_detail(self, obj):
        if (isinstance(obj, Parcel)):
            return ClientSerializer(obj.client_receiver).data
        return None

    def get_receiver_detail(self, obj):
        if (isinstance(obj, Parcel)):
            return UserSerializer(obj.receiver).data
        return None

    def get_sent_mail_detail(self, obj):
        if (isinstance(obj, Parcel)):
            return PostOfficeSerializer(obj.sent_mail).data
        return None

    def get_inbox_mail_detail(self, obj):
        if (isinstance(obj, Parcel)):
            return PostOfficeSerializer(obj.inbox_mail).data
        return None

    def validate(self, data):
        request = self.context.get('request')
        client_sender = data.get('client_sender')
        client_receiver = data.get('client_receiver')
        sender = data.get('sender')
        receiver = data.get('receiver')
        sent_mail = data.get('sent_mail')
        inbox_mail = data.get('inbox_mail')
        if request.method == 'POST':
            if not client_sender and not sender:
                raise serializers.ValidationError({'sender': 'required', 'client_sender': 'required'})
            if not client_receiver and not receiver:
                raise serializers.ValidationError({'receiver': 'required', 'client_receiver': 'required'})
        if client_receiver and client_sender and client_sender == client_receiver:
            raise serializers.ValidationError({'client_receiver':'client to same!'})
        if receiver and sender and sender == receiver:
            raise serializers.ValidationError({'receiver':'user to same!'})

        if inbox_mail and sent_mail and sent_mail == inbox_mail:
            raise serializers.ValidationError({'inbox_mail':'postoffice_to_same!'})
        return data

class ShoppingSerializer(serializers.ModelSerializer):
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    receiver_detail = serializers.SerializerMethodField()

    sent_mail = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all(), required=False)
    sent_mail_detail = serializers.SerializerMethodField()

    inbox_mail = serializers.PrimaryKeyRelatedField(queryset=PostOffice.objects.all(), required=False)
    inbox_mail_detail = serializers.SerializerMethodField()
    class Meta:
        model = Shopping
        fields = '__all__'
        ordering = ['-created_at']
        extra_kwargs = {
            'postage': {
                'required': True
            },
        }

    def get_sent_mail_detail(self, obj):
        return StoreSerializer(obj.sent_mail).data

    def get_receiver_detail(self, obj):
        return UserSerializer(obj.receiver).data

    def get_inbox_mail_detail(self, obj):
        return PostOfficeSerializer(obj.inbox_mail).data

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'
        depth = 2