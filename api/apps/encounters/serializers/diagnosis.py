from datetime import datetime
from rest_framework import serializers

from .. import models


class DiagnosisValueSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        required=True, choices=models.DiagnosisStatus.choices
    )
    diagnosis = serializers.DictField(required=True)


class DiagnosisSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    value = DiagnosisValueSerializer()
    created_at = serializers.DateTimeField()
    created_by = serializers.DictField()
