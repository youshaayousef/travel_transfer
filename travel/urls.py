from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'stations', StationViewSet)
router.register(r'buses', BusViewSet)
router.register(r'seats', SeatViewSet)
router.register(r'journeys', JourneyViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'reservation/details', ReservationDetailsViewSet)


urlpatterns = [
    path('viewset/v1/', include(router.urls)),
]