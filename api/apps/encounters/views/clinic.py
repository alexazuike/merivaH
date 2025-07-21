from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from .. import models, serializers, filters as enc_filters


class ClinicViewSet(viewsets.ModelViewSet):
    queryset = models.Clinic.objects.all()
    serializer_class = serializers.ClinicSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = enc_filters.ClinicFilter
    ordering_fields = ["name", "department"]
    ordering = ["-id"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializers.ClinicResponseSerializer
        return super().get_serializer_class()
