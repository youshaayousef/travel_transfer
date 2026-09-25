from django.shortcuts import render

# Create your views here.

from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()

from .serializers import *
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminUser]