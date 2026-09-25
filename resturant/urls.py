from django.urls import path, include
from .views import *

urlpatterns = [
    path('apiview/resturant/', ResturantAPIView.as_view()),
]