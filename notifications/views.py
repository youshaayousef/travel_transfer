from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
# Create your views here.

from .models import *
from .serializers import *
from .paginations import NotificationPagination

class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminUser]
    ordering = ['-created_at']
    pagination_class = NotificationPagination

    @action(methods=['get','delete'], detail=True, permission_classes=[IsAuthenticated])
    def user(self, request, pk=None):
        queryset = get_object_or_404(Notification,user=request.user, pk=pk)
        serializer = self.get_serializer(queryset)

        if request.method == 'GET':
            return Response(serializer.data)
        elif request.method == 'DELETE':
            self.perform_destroy(queryset)
            return Response(status=HTTP_204_NO_CONTENT)


    @action(methods=['get'],detail=False, permission_classes=[IsAuthenticated])
    def users(self, request):
        queryset = Notification.objects.filter(user=self.request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

class Remainder(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        from django.utils import timezone
        today = timezone.now().date()
        reservation = Reservation.objects.filter(
            user=user,
            created_at__date=today,
        )
        reservation_remainder = []
        from travel.models import ReservationDetails
        for i in reservation:
            if reservation_detail:
                reservation_remainder.append({
                    "id": i.id,
                    "reservation":i.reservationdetails_set.first().journey.departure_datetime,
                })
        parcel = Parcel.objects.filter(
            in_inbox_mail__isnull=False,
        ).filter(
            receiver=user,
            in_inbox_mail__date=today,
        )
        parcel_remainder = []
        for i in parcel:
            parcel_remainder.append({
                "id": i.id,
                "parcel":i.in_inbox_mail
            })
        return Response({
            "reservations":reservation_remainder,
            "parcels":parcel_remainder,
        }, status=HTTP_200_OK)