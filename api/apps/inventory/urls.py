from django.urls import path, include
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register("categories", views.CategoryViewSet)
router.register("stores", views.StoreViewset)
router.register("products", views.ProductViewSet)
router.register("stock_movements", views.StockMovementViewSet)
router.register("stock", views.StockViewSet)

stock_movement_router = routers.NestedDefaultRouter(
    router, r"stock_movements", lookup="movement"
)
stock_movement_router.register(
    r"lines", views.StockMovementLineViewSet, basename="movement-lines"
)

urlpatterns = [
    path("", include(router.urls)),
    path(r"", include(stock_movement_router.urls)),
]
