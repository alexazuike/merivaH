import uuid
from rest_framework import serializers

from api.apps.finance import models
from api.includes import exceptions
from api.includes import utils


class RevenueSummarySerializer(serializers.Serializer):
    module = serializers.CharField(required=True)
    total_amount = serializers.DecimalField(max_digits=125, decimal_places=2)
    count = serializers.IntegerField()


class RevenueDetailSerializer(serializers.Serializer):
    bill_source = serializers.CharField(required=True)
    bill_item_code = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    total_quantity = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=125, decimal_places=2)
    count = serializers.IntegerField()
