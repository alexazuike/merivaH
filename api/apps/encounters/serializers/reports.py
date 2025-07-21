from datetime import datetime

from rest_framework import serializers

from .. import models
from ..libs.encounter_report_generator import EncounterReportStruct


class EncounterReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Encounter
        fields = "__all__"
        read_only_fields = (
            "encounter_id",
            "bill",
            "acknowledged_by",
            "acknowledged_at",
        )

    def to_representation(self, instance):
        report_struct = EncounterReportStruct.initialize(instance)
        return report_struct.to_response_struct()
