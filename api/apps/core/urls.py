from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register("salutations", views.SalutationListView)
router.register("gender", views.GenderListView)
router.register("countries", views.CountryListView)
router.register("states", views.StateListView)
router.register("lgas", views.LGAListView)
router.register("districts", views.DistrictListView)
router.register("occupations", views.OccupationListView)
router.register("marital-status", views.MaritalStatusListView)
router.register("religion", views.ReligionListView)
router.register("templates", views.TemplateView)
router.register("diagnosis", views.DiagnosisView)
router.register("service_arms", views.ServiceArmsView)
router.register("preferences", views.AppPrefencesView)
router.register("document_types", views.DocumentTypeView)

urlpatterns = [
    path("", include(router.urls)),
]
