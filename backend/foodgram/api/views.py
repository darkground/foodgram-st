from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import pagination

from core.models import User
from .serializers import UserSerializer

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = pagination.LimitOffsetPagination