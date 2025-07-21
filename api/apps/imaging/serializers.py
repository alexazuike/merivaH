import json, io
from typing import List
from datetime import datetime

from django.utils import timezone
from rest_framework import serializers
from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile

from api.apps.finance import serializers as finance_serializers
from api.apps.finance import models as finance_models
from api.apps.finance import utils as finance_utils
from api.apps.core import serializers as core_serializers
from api.apps.patient import models as patient_models
from api.includes import utils, exceptions, file_utils
from .utils import get_imaging_obv_order_data, has_observation_order_status_perm
from .libs.imaging_report_generator import ImagingReportStruct
from .libs.imaging_obv_orders_factory import ImagingObvOrderFactory
from . import models


class ServiceCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ServiceCenter
        fields = "__all__"


class ModalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Modality
        fields = "__all__"


class ImagingObservationSerializer(serializers.ModelSerializer):
    modality = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=models.Modality.objects.all(),
    )
    bill_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True, allow_null=True, default=0
    )
    cost_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True, allow_null=True, default=0
    )

    class Meta:
        model = models.ImagingObservation
        fields = (
            "id",
            "name",
            "active",
            "modality",
            "status",
            "created_at",
            "bill_item_code",
            "bill_price",
            "cost_price",
        )
        depth = 1
        read_only_fields = [
            "bill_item_code",
        ]

    def create(self, validated_data):
        bill_price = validated_data.pop("bill_price", None)
        cost_price = validated_data.pop("cost_price", None)

        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        fields = self.context["request"].data
        validated_data["audit_log"] = [
            utils.AuditLog(
                user=user_data, event=utils.AuditEvent.CREATE, fields=fields
            ).dict()
        ]

        with transaction.atomic():
            imaging_observation: models.ImagingObservation = models.ImagingObservation(
                **validated_data
            )
            imaging_observation._created_by = user_data
            imaging_observation._bill_price = bill_price
            imaging_observation._cost_price = cost_price
            imaging_observation.save()
            return imaging_observation

    def update(self, instance: models.ImagingObservation, validated_data: dict):
        with transaction.atomic():
            bill_price = validated_data.pop("bill_price", None)
            cost_price = validated_data.pop("cost_price", None)
            user = self.context["request"].user
            user_data = utils.trim_user_data(utils.model_to_dict(user))
            fields = self.context["request"].data
            audit_data = utils.AuditLog(
                user=user_data, event=utils.AuditEvent.CREATE, fields=fields
            ).dict()

            instance.name = validated_data.get("name", instance.name)
            instance.active = validated_data.get("active", instance.active)
            instance.modality = validated_data.get("modality", instance.modality)
            instance.status = validated_data.get("status", instance.status)
            instance.audit_log.append(audit_data)
            instance._bill_price = bill_price
            instance._cost_price = cost_price
            instance.save()
            return instance


class ImgObvModalityGroup(serializers.Serializer):
    modality = serializers.CharField(max_length=256, required=True)
    img_observations = ImagingObservationSerializer(many=True)


class ImagingObvResponseSerializer(serializers.ModelSerializer):
    bill_price = serializers.SerializerMethodField(read_only=True)
    cost_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.ImagingObservation
        fields = "__all__"
        depth = 1

    def get_bill_price(self, obj):
        try:
            bill_item = finance_models.BillableItem.objects.get(
                item_code=obj.bill_item_code
            )
            return str(bill_item.selling_price)
        except finance_models.BillableItem.DoesNotExist:
            return None

    def get_cost_price(self, obj):
        try:
            bill_item = finance_models.BillableItem.objects.get(
                item_code=obj.bill_item_code
            )
            return str(bill_item.cost)
        except finance_models.BillableItem.DoesNotExist:
            return None


class ImagingOrderSerializer(serializers.ModelSerializer):
    payment_scheme = serializers.IntegerField(
        required=False, write_only=True, allow_null=True
    )

    img_obv = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.ImagingObservation.objects.all(), write_only=True
    )

    img_obv_orders = serializers.SerializerMethodField(read_only=True)
    diagnosis = core_serializers.DiagosisSerializer(required=False, many=True)

    class Meta:
        model = models.ImagingOrder
        fields = "__all__"
        read_only_fields = [
            "img_id",
            "img_obv_orders",
            "ordered_by",
            "ordered_datetime",
        ]

    def get_img_obv_orders(self, obj):
        obv_orders = get_imaging_obv_order_data(obj.id)
        return obv_orders

    def create(self, validated_data: dict):
        with transaction.atomic():
            user = self.context["request"].user
            user_data = utils.trim_user_data(utils.model_to_dict(user))
            audit_fields = self.context["request"].data
            validated_data["ordered_by"] = user_data
            img_obvs: List[models.ImagingObservation] = validated_data.pop("img_obv")
            validated_data["img_obv"] = [img_obv.id for img_obv in img_obvs]
            validated_data["diagnosis"] = json.loads(
                json.dumps(validated_data.get("diagnosis", []))
            )

            # gets payment scheme if added
            payment_scheme = validated_data.pop("payment_scheme", None)
            if payment_scheme:
                payment_scheme = finance_models.PayerScheme.objects.get(
                    id=payment_scheme
                )
            # save imaging order
            img_order = models.ImagingOrder.objects.create(**validated_data)

            img_obv_order_factory = ImagingObvOrderFactory(
                img_order_id=img_order.id,
                img_obvs=img_obvs,
                user_data=user_data,
                audit_fields=audit_fields,
                payment_scheme=payment_scheme,
            )

            img_obv_orders = img_obv_order_factory.populate_img_obv_orders()
            img_obv_orders_id = [
                img_obv_order.id
                for img_obv_order in img_obv_orders
                if img_obv_order is not None
            ]

            img_order.img_obv_orders.extend(img_obv_orders_id)
            img_order.save()
            return img_order


class ImagingObservationOrderSerializer(serializers.ModelSerializer):
    bill = serializers.SerializerMethodField(read_only=True)
    img_order = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=models.ImagingOrder.objects.all(),
    )
    comments = serializers.CharField(required=False, allow_null=True, write_only=True)

    def get_bill(self, obj):
        if obj.bill:
            bill_obj = finance_models.Bill.objects.get(id=int(obj.bill))
            data = finance_serializers.BillSerializer(bill_obj).data
            return finance_utils.clean_bill_details(data)
        return {"cleared_status": "CLEARED"}

    class Meta:
        model = models.ImagingObservationOrder
        fields = "__all__"
        depth = 1
        read_only_fields = (
            "audit_log",
            "bill",
            "approved_by",
            "approved_on",
            "reported_by",
            "reported_on",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        audit_fields = self.context["request"].data
        validated_data.pop("comments", None)

        audit_log = [
            utils.AuditLog(
                user=user_data,
                event=utils.AuditEvent.CREATE,
                fields=audit_fields,
            ).dict()
        ]
        validated_data["audit_log"] = audit_log
        img_obv_order = models.ImagingObservationOrder.objects.create(**validated_data)

        # update img_order
        img_order = models.ImagingOrder.objects.get(id=img_obv_order.img_order)
        img_order.img_obv_orders.append(img_obv_order.id)
        img_order.img_obvs.append(img_obv_order.img_obv["id"])
        img_order.save()

        return img_obv_order

    def update(self, instance, validated_data: dict):
        user = self.context["request"].user
        user_data = utils.trim_user_data(utils.model_to_dict(user))
        audit_fields = self.context["request"].data
        validated_data.pop("comments", None)

        if validated_data.get("status"):
            status = validated_data.get("status")
            if not has_observation_order_status_perm(user, status):
                raise exceptions.PermissionDenied(
                    "You do not have permission to perform this action"
                )

        if validated_data.get("status", "").casefold() == "CAPTURED".casefold():
            instance.reported_by = user_data
            instance.reported_on = timezone.now()

        if validated_data.get("status", "").casefold() == "APPROVED".casefold():
            instance.approved_by = user_data
            instance.approved_on = timezone.now()

        instance.img_order = validated_data.get("img_order", instance.img_order)
        instance.img_obv = validated_data.get("img_obv", instance.img_obv)
        instance.status = validated_data.get("status", instance.status)
        instance.report = validated_data.get("report", instance.report)
        instance.audit_log.append(
            utils.AuditLog(
                user=user_data,
                event=utils.AuditEvent.UPDATE,
                fields=audit_fields,
            ).dict()
        )
        instance.save()

        return instance


class ImagingObvOrderResponseSerializer(serializers.ModelSerializer):
    bill = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.ImagingObservationOrder
        fields = "__all__"
        depth = 1
        read_only_fields = ("audit_log", "bill")

    def get_bill(self, obj):
        if obj.bill:
            bill_obj = finance_models.Bill.objects.get(id=int(obj.bill))
            data = finance_serializers.BillSerializer(bill_obj).data
            return finance_utils.clean_bill_details(data)
        return {"cleared_status": "CLEARED"}


class ImagingObservationOrderReportsSerializer(serializers.ModelSerializer):
    img_order = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=models.ImagingOrder.objects.all(),
    )
    comments = serializers.CharField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = models.ImagingObservationOrder
        fields = "__all__"
        read_only_fields = (
            "audit_log",
            "approved_by",
            "approved_on",
            "reported_by",
            "reported_on",
        )

    def to_representation(self, instance):
        report_struct = ImagingReportStruct.initialize(instance)
        return report_struct.to_response_struct()


class ImagingObservationOrderAttachmentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=256, write_only=True, allow_empty_file=False
    )

    class Meta:
        model = models.ImagingObserverOrderAttachments
        fields = "__all__"
        read_only_fields = ("created_by", "updated_by", "file_path", "img_obv_order")

    def _get_patient(self, patient_dict: dict):
        try:
            return patient_models.Patient.objects.get(id=patient_dict.get("id"))
        except patient_models.Patient.DoesNotExist:
            raise exceptions.BadRequest("Patient does not exist")

    def create(self, validated_data):
        file_upload: InMemoryUploadedFile = validated_data.get("file")
        img_obv_order: models.ImagingObservationOrder = self.context["img_obv_order"]
        patient = self._get_patient(img_obv_order.patient)
        file_content: io.BytesIO = file_upload.read()
        saved_file_path = file_utils.FileUtils().upload_static_file(
            file_utils.StaticFolderType.PATIENT,
            str(patient.pk),
            file_upload.name,
            file_content,
        )
        user_details = utils.trim_user_data(
            utils.model_to_dict(self.context["request"].user)
        )
        return models.ImagingObservationOrder.objects.create(
            img_obv_order=img_obv_order,
            file_path=saved_file_path,
            created_by=user_details,
        )

    def update(self, instance, validated_data):
        file_upload: InMemoryUploadedFile = validated_data.get("file")
        img_obv_order: models.ImagingObservationOrder = self.context["img_obv_order"]
        user_details = utils.trim_user_data(
            utils.model_to_dict(self.context["request"].user)
        )

        if file_upload:
            file_content: io.BytesIO = file_upload.read()
            # upload new file

            new_file_path = file_utils.FileUtils().upload_static_file(
                file_utils.StaticFolderType.PATIENT,
                instance.patient.id,
                file_upload.name,
                file_content,
            )
            instance.file_path = new_file_path
            file_utils.FileUtils().remove_static_file(instance.file_path)
        instance.img_obv_order = img_obv_order or instance.img_obv_order
        instance.updated_by = user_details
        instance.save()
        return instance
