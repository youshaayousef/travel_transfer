from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('profiles', ProfileViewSet, basename='profile')

urlpatterns = [
    path('viewset/v1/', include(router.urls)),
]