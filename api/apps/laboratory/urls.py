from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register("service_center", views.ServiceCenterViewSet)
router.register("lab_observation", views.LabObservationViewSet)
router.register("lab_panel", views.LabPanelViewSet)
router.register("lab_specimen_type", views.LabSpecimenTypeViewSet)
router.register("lab_specimen", views.LabSpecimenViewSet)
router.register("lab_unit", views.LabUnitViewSet)
router.register("lab_order", views.LabOrderViewSet)
router.register("lab_panel_order", views.LabPanelOrderViewSet)
router.register("reports", views.LabReportsViewset)


urlpatterns = [
    path("", include(router.urls)),
]
