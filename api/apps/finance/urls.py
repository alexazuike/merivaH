from django.urls import path, include
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()

router.register("billable_items", views.BillableItemViewSet)
router.register("bills", views.BillViewSet)
router.register("price_lists", views.PriceListViewSet)
router.register("price_list_items", views.PriceListItemViewSet)
router.register("payers", views.PayerViewSet)
router.register("payer_schemes", views.PayerSchemeViewSet)
router.register("payment_methods", views.PaymentMethodViewSet)
router.register("payments", views.PaymentViewSet)
router.register("invoices", views.InvoiceViewSet)
router.register("cashbooks", views.CashbookViewSet)
router.register("reports/revenue/detailed", views.RevenueDetailedViewSet)
router.register("reports/revenue/summary", views.RevenueSummaryViewSet)
router.register("reports/payments/detailed", views.PaymentDetailReportViewset)
router.register("reports/payments/summary", views.PaymentSummaryReportViewset)
router.register("packages", views.BillPackageViewset)
router.register("package_subscriptions", views.PatientBillPackageSubViewset)

package_subscription_router = routers.NestedDefaultRouter(
    router, r"package_subscriptions", lookup="subscription"
)
package_subscription_router.register(
    r"usages", views.PatientBillPackageUsageViewset, basename="usages"
)

urlpatterns = [
    path("", include(router.urls)),
    path(r"", include(package_subscription_router.urls)),
]
