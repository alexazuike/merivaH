from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register("patients", views.PatientViewSet)
router.register("reports", views.PatientsReportsViewSet)
router.register("files", views.PatientFileViewset)

urlpatterns = [
    path("", include(router.urls)),
]
