from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register("facilities", views.FacilityViewSet)
router.register("departments", views.DepartmentViewSet)

urlpatterns = [path("", include(router.urls))]
