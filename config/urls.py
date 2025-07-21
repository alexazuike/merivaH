from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Swagger documentation endpoint
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # App endpoints
    # user endpoints
    path("api/v1/users/", include("api.apps.users.urls")),
    # auth app endpoints
    path("api/v1/auth/", include("api.apps.authentication.urls")),
    # core app endpoint
    path("api/v1/core/", include("api.apps.core.urls")),
    # patient app endpoint
    path("api/v1/patient/", include("api.apps.patient.urls")),
    # facilities app endpoint
    path("api/v1/facilities/", include("api.apps.facilities.urls")),
    # Encounters app endpoint
    path("api/v1/encounters/", include("api.apps.encounters.urls")),
    # Laboratory app endpoint
    path("api/v1/laboratory/", include("api.apps.laboratory.urls")),
    # Imaging app endpoint
    path("api/v1/imaging/", include("api.apps.imaging.urls")),
    # Finances app endpoint
    path("api/v1/finance/", include("api.apps.finance.urls")),
    # Pharmacy app endpoints
    path("api/v1/pharmacy/", include("api.apps.pharmacy.urls")),
    # Inventory app endpoints
    path("api/v1/inventory/", include("api.apps.inventory.urls")),
    # Nursing station endpoints
    path("api/v1/nursing/", include("api.apps.nursing.urls")),
    # Messaging app endpoints
    path("api/v1/messaging/", include("api.apps.messaging.urls")),
]

# Admin Site config
admin.site.site_header = "Health Application Administration"
admin.site.index_title = "Health App Admin"
