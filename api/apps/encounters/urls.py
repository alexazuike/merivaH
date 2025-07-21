from django.urls import path, include
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()

router.register("clinic", views.ClinicViewSet)
router.register("reports", views.EncounterReportsViewset)
router.register("templates", views.EncounterTemplateViewSet)
router.register("", views.EncounterViewSet)

encounter_nested_router = routers.NestedDefaultRouter(router, r"", lookup="encounter")
encounter_nested_router.register(
    r"orders", views.EncounterOrderViewset, basename="orders"
)
encounter_nested_router.register(
    r"vitals", views.EncounterVitalsViewset, basename="vitals"
)
encounter_nested_router.register(
    r"diagnosis", views.EncounterDiagnosisViewset, basename="diagnosis"
)
encounter_nested_router.register(
    r"charts", views.EncounterChartsViewset, basename="charts"
)


urlpatterns = [
    path("", include(router.urls)),
    path("", include(encounter_nested_router.urls)),
    path("get_providers/<slug:group_name>/", views.get_providers),
    path("get_patient_encounter/<int:patient_id>/", views.get_all_patients_encounter),
    path("<slug:status>/count/", views.get_encounter_status_count),
]
