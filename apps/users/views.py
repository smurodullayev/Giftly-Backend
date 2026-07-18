from rest_framework import viewsets, permissions
from .models import User, BusinessProfile, CourierProfile
from .serializers import UserSerializer, BusinessProfileSerializer, CourierProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class BusinessProfileViewSet(viewsets.ModelViewSet):
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class CourierProfileViewSet(viewsets.ModelViewSet):
    queryset = CourierProfile.objects.all()
    serializer_class = CourierProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
