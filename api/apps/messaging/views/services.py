from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .. import models, serializers


class MessageServiceViewset(viewsets.ModelViewSet):
    queryset = models.MessageService.objects.all()
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = [
        "name",
    ]
    ordering = ["-id"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializers.MessageResponseServiceSerializer
        return serializers.MessageRequestServiceSerializer
