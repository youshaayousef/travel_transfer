from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'postoffices', PostOfficeViewSet)
router.register(r'parcels', ParcelViewSet)
router.register(r'shopping', ShoppingViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'governorates', GovernorateViewSet)
router.register(r'cities', CityViewSet)

urlpatterns = [
    path('viewset/v1/', include(router.urls)),
    path('apiview/store/category/', StoreCategory.as_view()),
]