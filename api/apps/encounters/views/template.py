from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .. import models, serializers, filters as enc_filters


class EncounterTemplateViewSet(viewsets.ModelViewSet):
    queryset = models.EncounterTemplate.objects.all()
    serializer_class = serializers.EncounterTemplateSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = enc_filters.EncounterTemplateFilter
