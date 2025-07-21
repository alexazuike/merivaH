import re, json, string, pytz
from datetime import datetime, timezone
from enum import Enum
from functools import reduce
from typing import Mapping, Union, Set, TypeVar, Type, Iterable, Dict

from django.db import connection, models
from django.db.models.base import ModelBase
from django.db.models import Model
from django.db.models.query import QuerySet
from dateutil import parser
from django.utils import timezone
from pydantic import BaseModel, ValidationError, Field
from rest_framework_recursive.fields import RecursiveField
from rest_framework import serializers

from api.includes import exceptions
from config.preferences import AppPreferences


DJANGO_MODEL = TypeVar("DJANGO_MODEL", bound=Model)
PYDANTIC_SCHEMA = TypeVar("PYDANTIC_SCHEMA", bound=BaseModel)


def jsonfield_default_value():
    return dict(vitals=[], ros=[], exam=[], diag=[], orders={}, plan=[])


def provider_jsonfield_default_value():
    return dict(provider=[])


def time_log_jsonfield_default_value():
    return {"date_time": []}


def get_status(self):
    if self.is_active == True:
        return {"status": "active"}
    else:
        return {"status": "inactive"}


def extract_audit_log_data(
    audit_log: list,
    values: dict,
    params_after: dict = {},
    with_comments: bool = False,
    use_datetime: bool = False,
):
    """Extracts audit log using values as params"""
    data = {}
    params = values.copy()
    params = {str(key).casefold(): value for key, value in params.items()}
    params_to_search = list(params.keys())
    params_after_fields_search = list(params_after.keys())
    params_after_items = {
        str(key).casefold(): value for key, value in params_after.items()
    }

    for log in audit_log:
        full_name = f"""{log.get("user").get("first_name")} {log.get("user").get("last_name")}"""
        date_time = datetime.fromisoformat(log.get("date_time")).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        if use_datetime:
            date_time = datetime.fromisoformat(log.get("date_time"))

        if (
            log.get("event") == "update"
            and str(log.get("fields", {}).get("status", "")).strip().casefold()
            in params_to_search
        ):
            status: str = log.get("fields", {}).get("status")
            param: str = params.get(status.casefold())
            param = param.replace(" ", "_")
            data[f"{param}_by"] = full_name
            data[f"{param}_at"] = date_time
            if with_comments:
                data[f"{param}_comments"] = log.get("fields", {}).get("comments", "")

        if (
            log.get("event") == "update"
            and str(log.get("fields", {}).get("status", "")).strip().casefold()
            in params_after_fields_search
        ):
            log_index = audit_log.index(log)
            prev_log = audit_log[log_index - 1]
            status: str = log.get("fields", {}).get("status")
            param: str = params_after_items.get(status.casefold())
            param = param.replace(" ", "_")
            data[f"{param}_by"] = full_name
            data[f"{param}_at"] = date_time
            if with_comments:
                data[f"{param}_comments"] = prev_log.get("fields", {}).get(
                    "comments", ""
                )
    return data


def parse_to_timezone_aware(date: datetime):
    local_tz = pytz.timezone(AppPreferences().company_timezone)
    return date.replace(tzinfo=pytz.utc).astimezone(local_tz)


def format_template_context(context_data: dict):
    datetime_suffix = ("_at", "_datetime", "_on", "_date")
    return {
        key: (
            value
            if not str(key).endswith(datetime_suffix)
            else parser.parse(value).strftime(AppPreferences().company_dateformat)
        )
        for key, value in context_data.items()
    }


def to_report_structure(data: list):
    return [
        {
            string.capwords(str(k).replace("_", " ")): (
                parse_to_timezone_aware(parser.parse(record[k])).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                if record[k] is not None and str(k).endswith("_at")
                else record[k]
            )
            for k in record
        }
        for record in data
    ]


def to_response_struct(data: dict):
    return {
        key: (
            value
            if not str(key).endswith("_at") or value is None
            else parser.parse(value)
        )
        for key, value in data.items()
    }


def is_table_exist(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT 1 FROM pg_tables WHERE tablename = '{table_name}'")
        return cursor.fetchone() is not None


def trim_user_data(user_data):
    user_data.pop("last_login", None)
    user_data.pop("is_superuser", None)
    user_data.pop("is_staff", None)
    user_data.pop("is_active", None)
    user_data.pop("date_joined", None)
    user_data.pop("groups", None)
    user_data.pop("user_permissions", None)
    user_data.pop("password", None)
    return user_data


def get_company_data() -> dict:

    app_data = AppPreferences()
    return {
        "mobile_number": app_data.company_phone,
        "mail": app_data.company_mail,
        "website": app_data.company_website,
        "address": app_data.company_address,
    }


def str_to_bool(value: Union[str, bool]) -> bool:
    if type(value) == str:
        truthy_values = ["true", "1", "yes"]
        return value.lower() in truthy_values
    return value


def model_to_dict(instance, exclude_fields: Set = set(), **kwargs):
    """
    Convert a model instance to dict.
    """

    class Serializer(serializers.ModelSerializer):
        if hasattr(instance, "parent"):
            parent = RecursiveField(allow_null=True)

        class Meta:
            model = type(instance)
            depth = 1
            exclude = tuple(exclude_fields)

    data = Serializer(instance).data
    parsed_data: dict = json.loads(json.dumps(data))
    parsed_data.update(kwargs)
    return parsed_data


def copy_dict(dict_obj: dict, keys: Iterable):
    return {key: value for key, value in dict_obj.items() if key in set(keys)}


def list_to_queryset(model: ModelBase, data: list) -> QuerySet:
    """Converts a list of objects to queryset"""
    if not isinstance(model, ModelBase):
        raise ValueError("%s must be Model" % model)
    if not isinstance(data, list):
        raise ValueError("%s must be List Object" % data)

    pk_list = [obj.pk for obj in data]
    return model.objects.filter(pk__in=pk_list)


def to_12_hour_format(date_time: datetime) -> str:
    """
    Convert a 24-hour time string to 12-hour time string.
    """
    format = "%Y-%m-%d %I:%M %p"
    return date_time.strftime(format)


def generate_sec_id(
    prefix: str,
    table_name: str,
    model: Type[DJANGO_MODEL],
    search_field: str,
    **filters,
) -> str:
    """
    Creates a date generated id

    Args:
        prefix: prefix for item code

    Returns:
        str: item code
    """
    CURRENT_YEAR = str(timezone.now().year)
    CURRENT_MONTH = str(timezone.now().month).zfill(2)
    pattern_string = f"{CURRENT_YEAR}{CURRENT_MONTH}"
    re_pattern = re.compile(f"{pattern_string}(.*)")
    serial_no = 1

    if is_table_exist(table_name):
        if model.objects.count() > 0:
            filter_kwargs = {
                f"{search_field}__contains": f"{CURRENT_YEAR}{CURRENT_MONTH}",
                **filters,
            }
            objects = model.objects.filter(**filter_kwargs)
            if objects.count() > 0:
                last_object = reduce(
                    lambda obj1, obj2: obj1 if obj1.id > obj2.id else obj2, objects
                )
                search_value = getattr(last_object, search_field)
                serial_no = int(re_pattern.findall(search_value)[-1]) + 1
    unique_id = f"{prefix}{CURRENT_YEAR}{CURRENT_MONTH}{serial_no}"
    return unique_id


def validate_schema(data: Mapping, schema: Type[PYDANTIC_SCHEMA]):
    try:
        if not isinstance(data, Mapping):
            raise TypeError("data must be a mapping type")
        return schema(**data)
    except ValidationError as e:
        raise exceptions.BadRequest(str(e))


class AuditEvent(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class AuditLog(BaseModel):
    user: dict
    event: AuditEvent
    fields: dict
    date_time: str = Field(default_factory=lambda: str(timezone.now()))


class Modules(str, Enum):
    ENCOUNTERS = "Encounter"
    IMAGING = "Imaging"
    LABORATORY = "Laboratory"
    INVENTORY = "Inventory"
    PHARMACY = "Pharmacy"
    NURSING = "Nursing"
    FINANCE = "Finance"
    MESSAGING = "Messaging"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    @classmethod
    def search_choices(cls):
        return tuple((i.value, i.name) for i in cls)

    @classmethod
    def get_module(cls, module_name: str):
        for item in cls:
            if str(item.value).casefold() == module_name.casefold():
                return item
        return None

    @classmethod
    def get_module_value(cls, module_code: str):
        for item in cls:
            if item.name.casefold() == module_code.casefold():
                return item.value
        return None

    @classmethod
    def module_names(cls):
        return [i.name for i in cls]

    @classmethod
    def module_values(cls):
        return [i.value for i in cls]

    def __str__(self):
        return self.value


class ContextFormatter:
    def __init__(self, context_data: dict) -> None:
        self.context_data = context_data.copy()
        self.datetime_suffix = ("_at", "_datetime", "_on", "_date")

    def _format_datetime(self, value: str) -> str:
        return parse_to_timezone_aware(parser.parse(value)).strftime(
            AppPreferences().company_dateformat
        )

    def _process_value(
        self, key: str, value: Union[str, list, dict]
    ) -> Union[str, list, dict]:
        if type(value) == str and key.endswith(self.datetime_suffix):
            return self._format_datetime(value)
        elif type(value) == dict:
            return {k: self._process_value(k, v) for k, v in value.items()}
        elif type(value) == list:
            return [self._process_value(key, item) for item in value]
        return value

    def process(self) -> dict:
        """
        Formats context data to conform
        with user app preferences.

        Returns:
            dict: formatted data
        """
        return self._process_value("", self.context_data)
