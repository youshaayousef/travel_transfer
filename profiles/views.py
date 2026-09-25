from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import *
from .serializers import *

class ProfileViewSet(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def get_object(self):
        return get_object_or_404(Profile,user=self.request.user)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)
