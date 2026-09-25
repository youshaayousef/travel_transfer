from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('viewset/v1/', include(router.urls)),
    path('api/remainder/', Remainder.as_view()),
]