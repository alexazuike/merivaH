from django.urls import path, include
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()

router.register("doses", views.DoseViewSet)
router.register("units", views.UnitViewSet)
router.register("routes", views.RouteViewSet)
router.register("frequencies", views.FrequencyViewSet)
router.register("directions", views.DirectionViewSet)
router.register("durations", views.DurationViewSet)
router.register("categories", views.CategoryViewSet)
router.register("generic_drugs", views.GenericDrugViewSet)
router.register("templates", views.TemplateViewSet)
router.register("stores", views.StoreViewSet)
router.register("prescriptions", views.PrescriptionViewSet)

prescription_details_router = routers.NestedDefaultRouter(
    router, r"prescriptions", lookup="detail"
)
prescription_details_router.register(
    r"details", views.PrescriptionDetailViewset, basename="prescription-details"
)


urlpatterns = [
    path("", include(router.urls)),
    path(r"", include(prescription_details_router.urls)),
]
