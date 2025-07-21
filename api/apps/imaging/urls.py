from django.urls import path, include
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()

router.register("service_center", views.ServiceCenterViewSet)
router.register("modality", views.ModalityViewSet)
router.register("imaging_observation", views.ImagingObservationViewSet)
router.register("imaging_order", views.ImagingOrderViewSet)
router.register("imaging_observation_order", views.ImagingObservationOrderViewSet)
router.register("reports", views.ImagingReportsViewset)

img_obv_order_router = routers.NestedDefaultRouter(
    router,
    r"imaging_observation_order",
    lookup="order",
)

img_obv_order_router.register(
    r"attachments",
    views.ImagingObservationOrderAttachmentsViewSet,
    basename="order-attachments",
)

urlpatterns = [
    path("", include(router.urls)),
    path(r"", include(img_obv_order_router.urls)),
]
