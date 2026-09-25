from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('gallery', GalleryViewSet, basename='gallery')

urlpatterns = [
    path('viewset/v1/', include(router.urls)),
]
