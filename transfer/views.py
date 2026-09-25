from django.shortcuts import render

# Create your views here.

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from django.db import transaction
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import *
from statement.models import Balance
from .serializers import *
from index.permissions import IsATMOrOnlyRead
from index.paginations import CustomPagination
@method_decorator(cache_page(60 * 60 * 2), name='dispatch')
class FeeViewSet(ReadOnlyModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer
    permission_classes = [AllowAny]
    from .paginations import FeePagination
    pagination_class = FeePagination

class GiftViewSet(ModelViewSet):
    queryset = Gift.objects.all()
    serializer_class = GiftSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filterset_fields = ['payer', 'payee', 'payer__username', 'payee__username']
    ordering = ["-created_at"]

    def get_queryset(self):
        return Gift.objects.filter(Q(payer=self.request.user)|Q(payee=self.request.user))


    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()

        data['payer'] = user.id
        data['payee'] = get_object_or_404(User, username=data['payee']).id
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            
            with transaction.atomic():
                balance_payer = user.balance.balance
                balance_payee = get_object_or_404(User, id=int(data["payee"])).balance.balance
                fee = get_object_or_404(Fee, min__lte=int(data["gift"]), max__gt=int(data["gift"]))
                price = fee.fee + int(data["gift"])
                if data['is_paid']=='on':
                    is_paid = True
                elif data['is_paid']=='false':
                    is_paid = False
                if (balance_payer < price and is_paid) or balance_payer < int(data['gift']):
                    return Response({"detail": "payer's balance not enough"}, status=HTTP_400_BAD_REQUEST)
                if balance_payee < fee.fee and not is_paid:
                    return Response({"detail": "payee's balance not enough"}, status=HTTP_400_BAD_REQUEST)
                serializer.save(price=price)
                return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['phone_number']

    def create(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_ATM or user.is_postmaster or user.is_superuser):
            return Response({"detail": "you not employee!"}, status=HTTP_400_BAD_REQUEST)
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response( serializer.errors, status=HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)


class UndirectTransferViewSet(ModelViewSet):
    queryset = UndirectTransfer.objects.all()
    serializer_class = UndirectTransferSerializer
    permission_classes = [IsATMOrOnlyRead]
    pagination_class = CustomPagination
    ordering = ["-created_at"]
    filterset_fields = ['payee_user', "payee__phone_number", "payer__phone_number"]
    #search_fields = ['id']

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()

        data["payer"] = get_object_or_404(Client, phone_number= data["payer"]).id
        if "payee_user" in data:
            data["payee_user"] = get_object_or_404(User, username=data["payee_user"]).id
        if "payee" in data:
            data["payee"] = get_object_or_404(Client, phone_number=data["payee"]).id
        transfer_employee = user.employee
        data['transfer_atm'] = transfer_employee.atm.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            fee = get_object_or_404(Fee,min__lte=int(data["amount"]), max__gt=int(data["amount"]))
            price = fee.fee + int(data["amount"])
            if "payee" in data:
                serializer.save(user=user, price=price)
                return Response(serializer.data, status=HTTP_201_CREATED)

            if data['is_paid'] == 'on':
                is_paid = True
            elif data['is_paid'] == 'false':
                is_paid = False

            if "payee_user" in data and is_paid:
                serializer.save(user=user, is_received=True, price=price)
                return Response(serializer.data, status=HTTP_201_CREATED)
            elif "payee_user" in data and not is_paid:
                payee_user = get_object_or_404(User,id=int(data['payee_user']))
                balance_payee_user = payee_user.balance.balance
                if balance_payee_user < fee.fee:
                    return Response({"detail": "payee's balance not enough"}, status=HTTP_400_BAD_REQUEST)
                serializer.save(user=user, is_received=True, price=price)
                return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    @action(methods=["patch"], detail=True, permission_classes=[IsATMOrOnlyRead])
    def delivery(self, request, pk=None):
        user = request.user
        data = request.data
        instance = get_object_or_404(UndirectTransfer, pk=pk)
        if instance.is_received:
            return Response({"detail": "already delivered"}, status=HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data = data, partial=True)
        from django.utils import timezone
        received_at = timezone.now()
        if serializer.is_valid():
            delivery_employee = user.employee
            if instance.delivery_atm != delivery_employee.atm:
                return Response({"detail": "you not employee here!"}, status=HTTP_400_BAD_REQUEST)
            serializer.save(delivery_employee=user, is_received=True, received_at=received_at)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)


class DirectTransferViewSet(ModelViewSet):
    queryset = DirectTransfer.objects.all()
    serializer_class = DirectTransferSerializer
    permission_classes = [IsATMOrOnlyRead]
    pagination_class = CustomPagination
    ordering = ["-created_at"]
    filterset_fields = ['payer']
    search_fields = ['id']

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()


        data["payee"] = get_object_or_404(Client, phone_number= data["payee"]).id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():
                balance = user.balance.balance
                fee = get_object_or_404(Fee,min__lte=int(data["amount"]), max__gt=int(data["amount"]))
                price = fee.fee + int(data["amount"])
                if data['is_paid'] == 'on':
                    is_paid = True
                elif data['is_paid'] == 'false':
                    is_paid = False
                if (balance < price and is_paid) or balance < int(data['amount']):
                    return Response({"detail": "balance not enough"}, status=HTTP_400_BAD_REQUEST)
                serializer.save(payer=user, price=price)
                return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True, permission_classes=[IsATMOrOnlyRead])
    def delivery(self, request, pk=None):
        user = request.user
        data = request.data
        instance = get_object_or_404(DirectTransfer, pk=pk)
        if instance.is_received:
            return Response({"detail": "already delivery"}, status=HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data = data, partial=True)
        from django.utils import timezone
        received_at = timezone.now()
        if serializer.is_valid():
            delivery_employee = user.employee
            if instance.delivery_atm != delivery_employee.atm:
                return Response({"detail": "you not employee here"}, status=HTTP_400_BAD_REQUEST)
            serializer.save(delivery_employee=user, is_received=True, received_at=received_at)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)
