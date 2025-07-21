from django.urls import path, include
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register("stations", views.NursingStationViewset)
router.register("services", views.NursingServiceViewSet)
router.register("orders", views.NursingOrderViewSet)

task_router = routers.NestedDefaultRouter(router, r"orders", lookup="order")
task_router.register(r"tasks", views.NursingTaskViewSet, basename="tasks")

urlpatterns = [
    path("", include(router.urls)),
    path(r"", include(task_router.urls)),
]
