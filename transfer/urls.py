from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'fees', FeeViewSet)
router.register(r'gifts', GiftViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'undirect_transfers', UndirectTransferViewSet)
router.register(r'direct_transfers', DirectTransferViewSet)

urlpatterns = [
    path('viewset/v1/', include(router.urls)),
]