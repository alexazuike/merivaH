from rest_framework import viewsets
from rest_framework import filters as rf_filters
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import *
from . import models
from . import filters


class SalutationListView(viewsets.ReadOnlyModelViewSet):
    queryset = models.Salutation.objects.all()
    serializer_class = SalutationSerializer


class GenderListView(viewsets.ReadOnlyModelViewSet):
    queryset = models.Gender.objects.all()
    serializer_class = GenderSerializer


class CountryListView(viewsets.ReadOnlyModelViewSet):
    queryset = models.Country.objects.all()
    serializer_class = CountrySerializers


class StateListView(viewsets.ReadOnlyModelViewSet):
    queryset = models.State.objects.all()
    serializer_class = StateSerializers
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["country"]


class LGAListView(viewsets.ReadOnlyModelViewSet):
    queryset = models.LGA.objects.all()
    serializer_class = LGASerializers
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["state"]


class DistrictListView(viewsets.ReadOnlyModelViewSet):
    queryset = models.District.objects.all()
    serializer_class = DistrictSerializers
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["state"]


class OccupationListView(viewsets.ReadOnlyModelViewSet):
    queryset = models.Occupation.objects.all()
    serializer_class = OccupationSerializers


class MaritalStatusListView(viewsets.ReadOnlyModelViewSet):
    queryset = models.MaritalStatus.objects.all()
    serializer_class = MaritalStatusSerializer


class ReligionListView(viewsets.ReadOnlyModelViewSet):
    queryset = models.Religion.objects.all()
    serializer_class = ReligionSerializer


class IdentityListView(viewsets.ReadOnlyModelViewSet):
    queryset = models.Identity.objects.all()
    serializer_class = IdentitySerializer


class TemplateView(viewsets.ModelViewSet):
    queryset = models.Template.objects.all()
    serializer_class = TemplateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.TemplateFilter


class DiagnosisView(viewsets.ReadOnlyModelViewSet):
    queryset = models.Diagnosis.objects.all()
    serializer_class = DiagosisSerializer
    filter_backends = [
        DjangoFilterBackend,
        rf_filters.SearchFilter,
        rf_filters.OrderingFilter,
    ]
    search_fields = ["type", "case", "code"]
    filterset_class = filters.DiagnosisFilter


class ServiceArmsView(viewsets.ReadOnlyModelViewSet):
    queryset = models.ServiceArm.objects.all()
    serializer_class = ServiceArmSerializer


class AppPrefencesView(viewsets.ModelViewSet):
    queryset = models.AppPreferences.objects.all()
    serializer_class = AppPreferencesSerializer
    filter_backends = [
        DjangoFilterBackend,
        rf_filters.SearchFilter,
        rf_filters.OrderingFilter,
    ]
    filterset_class = filters.AppPreferencesFilter


class DocumentTypeView(viewsets.ModelViewSet):
    queryset = models.DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    filter_backends = [
        DjangoFilterBackend,
        rf_filters.SearchFilter,
        rf_filters.OrderingFilter,
    ]
    search_fields = ["name"]
