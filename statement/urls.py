from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('atms', ATMViewSet, basename='atms')
router.register('balance', BalanceViewSet, basename='balances')
router.register('deposits', DepositeViewSet, basename='deposits')
router.register('withdraws', WithdrawViewSet, basename='withdraws')

urlpatterns = [
    path('viewset/v1/', include(router.urls)),
]
