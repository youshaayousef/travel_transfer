# views.py
from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from index.paginations import CustomPagination
from index.permissions import IsATMOrOnlyRead
from .models import ATM, Balance, Deposit, Withdraw
from .paginations import ATMPagination
from .serializers import ATMSerializer, BalanceSerializer, DepositSerializer, WithdrawSerializer

User = get_user_model()


class ATMViewSet(ReadOnlyModelViewSet):
    queryset = ATM.objects.all()
    serializer_class = ATMSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['city']
    pagination_class = ATMPagination


class BalanceViewSet(ReadOnlyModelViewSet):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Balance.objects.filter(user=self.request.user)

    def get_object(self):
        return get_object_or_404(Balance, user=self.request.user)


class DepositeViewSet(ModelViewSet):
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer
    permission_classes = [IsATMOrOnlyRead]
    pagination_class = CustomPagination
    ordering = ['-datetime']

    def get_queryset(self):
        return Deposit.objects.filter(customer=self.request.user)

    def get_object(self):
        return get_object_or_404(Deposit, customer=self.request.user, pk=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()

        # Get the customer (account owner) by username
        customer = get_object_or_404(User, username=data.get('customer'))
        data['customer'] = customer.id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            # Save with the performing user (ATM operator) and the customer
            serializer.save(user=user, customer=customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)


class WithdrawViewSet(ModelViewSet):
    queryset = Withdraw.objects.all()
    serializer_class = WithdrawSerializer
    permission_classes = [IsATMOrOnlyRead]
    pagination_class = CustomPagination
    ordering = ['-datetime']

    def get_queryset(self):
        return Withdraw.objects.filter(customer=self.request.user)

    def get_object(self):
        return get_object_or_404(Withdraw, customer=self.request.user, pk=self.kwargs['pk'])

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()

        # Get the customer (account owner) by username
        customer = get_object_or_404(User, username=data.get('customer'))
        data['customer'] = customer.id

        # Validate amount
        try:
            amount = Decimal(data.get('amount', 0))
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response({"detail": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if customer has a balance
        try:
            balance = customer.balance.balance
        except Balance.DoesNotExist:
            return Response({"detail": "Customer has no balance record"}, status=status.HTTP_400_BAD_REQUEST)

        if balance < amount:
            return Response({"detail": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            # Save the withdrawal; later you might also update the balance here
            serializer.save(user=user, customer=customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)