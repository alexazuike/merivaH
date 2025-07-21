from django.shortcuts import render
from .models import Facility, Department
from .serializers import FacilitySerializer, DepartmentSerializer
from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.
class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["name", "state", "city", "lga"]
    ordering_fields = ["name", "city", "state"]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filer_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["name", "display_name"]
    ordering_fields = ["name", "display_name"]
