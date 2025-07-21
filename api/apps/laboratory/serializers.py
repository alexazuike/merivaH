from typing import List

from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from api.apps.finance import models as finance_models
from api.apps.finance import utils as finance_utils
from api.includes import utils
from . import models
from . import libs as lab_lib
from . import utils as lab_utils


class ServiceCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ServiceCenter
        fields = "__all__"


class LabObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LabObservation
        fields = "__all__"


class LabSpecimenTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LabSpecimenType
        fields = "__all__"


class LabSpecimenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LabSpecimen
        fields = "__all__"


class LabUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LabUnit
        fields = "__all__"


class LabPanelSerializer(serializers.ModelSerializer):
    specimen_type = serializers.PrimaryKeyRelatedField(
        queryset=models.LabSpecimenType.objects.all(), required=True
    )

    lab_unit = serializers.PrimaryKeyRelatedField(
        queryset=models.LabUnit.objects.all(), required=True
    )

    bill_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        allow_null=True,
        write_only=True,
    )

    cost_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = models.LabPanel
        exclude = ["audit_log"]
        depth = 1
        read_only_fields = [
            "bill_item_code",
        ]

    def validate_obv(self, value):
        if value:
            if not LabObservationSerializer(data=value, many=True).is_valid():
                raise serializers.ValidationError("Invalid observations")
        return value

    def create(self, validated_data):
        try:
            fields = self.context["request"].data
            user = self.context["request"].user
            user_data = utils.model_to_dict(user)

            bill_price = validated_data.pop("bill_price", None)
            cost_price = validated_data.pop("cost_price", None)
            validated_data.pop("template", None)
            validated_data["audit_log"] = [
                utils.AuditLog(
                    user=utils.trim_user_data(user_data),
                    event=utils.AuditEvent.CREATE,
                    fields=fields,
                ).dict()
            ]
            with transaction.atomic():
                lab_panel: models.LabPanel = models.LabPanel(**validated_data)
                lab_panel._created_by = user_data
                lab_panel._bill_price = bill_price
                lab_panel._cost_price = cost_price
                lab_panel.save()
                return lab_panel

        except (
            models.LabUnit.DoesNotExist or models.LabSpecimenType.DoesNotExist
        ) as e:
            if type(e) == models.LabUnit.DoesNotExist:
                raise serializers.ValidationError("Lab unit does not exist", code=404)
            else:
                raise serializers.ValidationError(
                    "Specimen type does not exist", code=404
                )

    def update(self, instance: models.LabPanel, validated_data: dict):
        with transaction.atomic():
            try:
                fields = self.context["request"].data
                bill_price = validated_data.pop("bill_price", None)
                cost_price = validated_data.pop("cost_price", None)
                user = self.context["request"].user
                user_data = utils.model_to_dict(user)

                instance.name = validated_data.get("name", instance.name)
                instance.obv = validated_data.get("obv", instance.obv)
                instance.active = validated_data.get("active", instance.active)
                instance.specimen_type = validated_data.get(
                    "specimen_type", instance.specimen_type
                )
                instance.lab_unit = validated_data.get("lab_unit", instance.lab_unit)
                instance.template = validated_data.get("template", instance.template)
                instance.audit_log.append(
                    utils.AuditLog(
                        user=utils.trim_user_data(user_data),
                        event=utils.AuditEvent.UPDATE,
                        fields=fields,
                    ).dict()
                )
                instance._bill_price = bill_price
                instance._cost_price = cost_price
                instance.save()
                return instance
            except (
                models.LabUnit.DoesNotExist,
                models.LabSpecimenType.DoesNotExist,
            ) as e:
                raise serializers.ValidationError(detail=str(e), code=404)


class LabPanelResponseSerializer(serializers.ModelSerializer):
    bill_price = serializers.SerializerMethodField(read_only=True)
    cost_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.LabPanel
        fields = "__all__"
        depth = 1

    def get_bill_price(self, obj):
        try:
            bill_item = finance_models.BillableItem.objects.get(
                item_code=obj.bill_item_code
            )
            return bill_item.selling_price
        except finance_models.BillableItem.DoesNotExist:
            return None

    def get_cost_price(self, obj):
        try:
            bill_item = finance_models.BillableItem.objects.get(
                item_code=obj.bill_item_code
            )
            return bill_item.cost
        except finance_models.BillableItem.DoesNotExist:
            return None


class LabPanelUnitGroup(serializers.Serializer):
    lab_unit = serializers.CharField(max_length=256, required=True)
    lab_panels = LabPanelSerializer(many=True)


class LabOrderSerializer(serializers.ModelSerializer):
    payment_scheme = serializers.IntegerField(
        required=False, write_only=True, allow_null=True
    )
    lab_panels = serializers.PrimaryKeyRelatedField(
        queryset=models.LabPanel.objects.all(),
        many=True,
        required=True,
        write_only=True,
    )
    lab_panel_orders = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.LabOrder
        fields = "__all__"
        read_only_fields = ["ordered_datetime", "ordered_by", "asn", "lab_panel_orders"]

    def get_lab_panel_orders(self, obj):
        panel_orders = list(
            models.LabPanelOrder.objects.filter(id__in=obj.lab_panel_orders)
        )
        panel_orders = lab_utils.get_lab_panel_order_data(*panel_orders)
        return panel_orders

    def create(self, validated_data):
        """
        Create a new lab order
        """
        with transaction.atomic():
            user = self.context["request"].user
            user_data = utils.trim_user_data(utils.model_to_dict(user))
            validated_data["ordered_by"] = user_data
            lab_panels: List[models.LabPanel] = validated_data.get("lab_panels")
            validated_data["lab_panels"] = [panel.id for panel in lab_panels]

            payment_scheme = validated_data.pop("payment_scheme", None)
            if payment_scheme:
                payment_scheme = finance_models.PayerScheme.objects.get(
                    id=payment_scheme
                )

            lab_order = models.LabOrder.objects.create(**validated_data)

            lab_panel_order_lib = lab_lib.LabPanelsAndOrders(
                lab_order_id=lab_order.id,
                lab_panels=lab_panels,
                user_data=user_data,
                audit_fields={},
                payment_scheme=payment_scheme,
            )

            lab_panel_orders = lab_panel_order_lib.populate_lab_panel_orders()
            lab_panel_orders_ids = [
                panel_order.id
                for panel_order in lab_panel_orders
                if panel_order is not None
            ]
            lab_order.lab_panel_orders = lab_panel_orders_ids
            lab_order.ordered_by = user_data
            lab_order.save()
            return lab_order


class LabPanelOrderSerializer(serializers.ModelSerializer):
    bill = serializers.SerializerMethodField()
    comments = serializers.CharField(
        required=False, write_only=True, allow_blank=True, allow_null=True
    )
    asn = serializers.SerializerMethodField()
    log = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.LabPanelOrder
        read_only_fields = [
            "bill",
            "asn",
            "approved_by",
            "approved_on",
            "is_result_sent",
            "log",
        ]
        exclude = [
            "panel_struct",
            "audit_log",
        ]

    def get_bill(self, obj):
        if obj.status.casefold() == lab_utils.LabPanelOrderStatus.CANCELLED.casefold():
            return None
        if obj.bill:
            bill_obj = finance_models.Bill.objects.get(id=int(obj.bill))
            data = utils.model_to_dict(bill_obj)
            return finance_utils.clean_bill_details(data)
        return {"cleared_status": "CLEARED"}

    def get_asn(self, obj):
        return obj.lab_order.asn

    def get_log(self, obj):
        audit_search_params = {
            "recieve specimen": "specimen_taken",
            "fill result": "specimen_recieved",
            "cancelled": "cancelled",
        }
        audit_after_search_params = {
            "awaiting approval": "result_submitted",
            "approved": "approved",
        }
        log_data = utils.extract_audit_log_data(
            obj.audit_log,
            audit_search_params,
            audit_after_search_params,
            with_comments=True,
        )
        return log_data

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context["request"].user
            user_data = utils.trim_user_data(utils.model_to_dict(user))
            fields = self.context["request"].data
            validated_data.pop("comments", None)

            try:
                validated_data["lab_order"] = models.LabOrder.objects.get(
                    id=self.context["lab_order"]
                )
                validated_data["audit_log"] = [
                    utils.AuditLog(
                        user=user_data,
                        event=utils.AuditEvent.CREATE,
                        fields=fields,
                    ).dict()
                ]
                lab_panel_order = models.LabPanelOrder.objects.create(**validated_data)
                return lab_panel_order

            except models.LabOrder.DoesNotExist as e:
                raise serializers.ValidationError(detail=str(e), code=404)

    def update(self, instance: "models.LabPanelOrder", validated_data: dict):
        with transaction.atomic():
            user = self.context["request"].user
            user_data = utils.trim_user_data(utils.model_to_dict(user))
            fields = self.context["request"].data
            validated_data.pop("comments", None)

            # check lab permissions status for this order
            if validated_data.get("status"):
                status = validated_data.get("status")
                if not lab_utils.has_panel_order_status_perm(user, status, instance):
                    raise PermissionDenied(
                        detail="You do not have permission to further change this order's status",
                        code=403,
                    )

            instance.panel = validated_data.get("panel", instance.panel)
            instance.patient = validated_data.get("patient", instance.patient)
            instance.status = validated_data.get("status", instance.status)

            instance.audit_log.append(
                utils.AuditLog(
                    user=user_data,
                    event=utils.AuditEvent.UPDATE,
                    fields=fields,
                ).dict()
            )

            if validated_data.get("status", "none").casefold() == "approved".casefold():
                instance.approved_by = user_data
                instance.approved_on = timezone.now()
                instance.panel_struct = lab_utils.to_panel_report_struct(instance.panel)

                # mail patient result on lab approval
                instance.mail_lab_result()

            instance.save()
            return instance


class LabPanelOrderObservationUpdateSerializer(serializers.Serializer):
    comments = serializers.CharField(
        max_length=255, required=False, allow_null=True, allow_blank=True
    )
    obv = serializers.ListField(child=serializers.DictField(), required=True)
    status = serializers.CharField(
        max_length=255, required=False, allow_null=True, allow_blank=True
    )


class LabPanelOrderReportsSerializer(serializers.ModelSerializer):
    comments = serializers.CharField(
        required=False, write_only=True, allow_blank=True, allow_null=True
    )

    class Meta:
        model = models.LabPanelOrder
        fields = "__all__"
        read_only_fields = [
            "audit_log",
            "approved_by",
            "approved_on",
            "is_result_sent",
        ]

    def to_representation(self, instance):
        report_struct = lab_lib.LabReportStruct.initialize(instance)
        return report_struct.to_response_struct()
