from . import models
from django_filters import rest_framework


class DiagnosisFilter(rest_framework.FilterSet):
    type = rest_framework.CharFilter(field_name="type", lookup_expr="icontains")
    case = rest_framework.CharFilter(field_name="case", lookup_expr="icontains")
    code = rest_framework.CharFilter(field_name="code", lookup_expr="icontains")

    class Meta:
        model = models.Diagnosis
        fields = ["type", "case", "code"]


class TemplateFilter(rest_framework.FilterSet):
    title = rest_framework.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = models.Template
        fields = ["title", "source"]


class AppPreferencesFilter(rest_framework.FilterSet):
    class Meta:
        model = models.AppPreferences
        fields = ["title", "type"]
