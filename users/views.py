from django.shortcuts import render
from rest_framework.request import Request

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *

from django.contrib.auth import get_user_model
User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Open to all users (no authentication required)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User registered successfully.",
                "user": serializer.data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth import authenticate

class LoginView(APIView):
    permission_classes = [AllowAny]  # Open to all users (no authentication required)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Authenticate user
            user = authenticate(username=username, password=password)
            if user:
                if user.is_blocked:
                    return Response(
                        {
                            "detail": "Your account is blocked."
                         },
                        status = status.HTTP_403_FORBIDDEN
                    )
                user_serializer = UserSerializer(user)
                # Generate tokens for the authenticated user
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Login successful.",
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    "user": user_serializer.data,
                }, status=status.HTTP_200_OK)
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.permissions import IsAuthenticated

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can log out

    def post(self, request):
        try:
            # Extract the refresh token from the request
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token to make it invalid
            return Response({"message": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Logout failed. Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            update_session_auth_hash(request, request.user)  # Keeps the user logged in
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateUserView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['username']

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        user = User.objects.get(id= self.kwargs.get("pk"))
        if request.user == user:
            return super().update(request, *args, **kwargs)
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs.get("pk"))
        if request.user == user:
            return super().partial_update(request, *args, **kwargs)
        return Response({"detail": "not allowed"}, status=status.HTTP_400_BAD_REQUEST)

from auth_kit.views import RegisterView
from .serializers import CustomRegisterSerializer

class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer
