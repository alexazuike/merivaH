from typing import Type

from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from api.includes import utils


class DictCharSerializerField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return value
        raise serializers.ValidationError("Value must be a dict or string")

    def to_internal_value(self, data):
        if isinstance(data, dict):
            return data
        if isinstance(data, str):
            return data
        raise serializers.ValidationError("Value must be a dict or string")


class ListDictCharSerializerField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return value
        raise serializers.ValidationError("Value must be a dict or string")

    def to_internal_value(self, data):
        if isinstance(data, dict):
            return data
        if isinstance(data, str):
            return data
        if isinstance(data, list):
            return data
        raise serializers.ValidationError("Value must be a dict or string")


class PkToDictRelatedSeriaizerField(serializers.RelatedField):
    default_error_messages = {
        "required": ("This field is required."),
        "does_not_exist": ('Invalid pk "{pk_value}" - object does not exist.'),
        "incorrect_type": ("Incorrect type. Expected pk value, received {data_type}."),
    }

    def __init__(self, **kwargs):
        self.pk_field = kwargs.pop("pk_field", None)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        queryset = self.get_queryset()
        try:
            if isinstance(data, bool):
                raise TypeError
            if isinstance(data, dict):
                object = queryset.get(pk=data.get("id"))
            if isinstance(data, int) or isinstance(data, str):
                object = queryset.get(pk=data)
            return utils.model_to_dict(
                object, exclude_fields={"created_at", "updated_at"}
            )
        except ObjectDoesNotExist:
            self.fail("does_not_exist", pk_value=data)
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)

    def to_representation(self, value):
        if value:
            if issubclass(type(value), models.Model):
                return utils.model_to_dict(value)
            if type(value) == dict:
                return value
            raise serializers.ValidationError(
                "Value must be either be an object of django model or dict"
            )
        return {}
