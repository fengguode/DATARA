"""Same-origin session and read-only saved-metric routes (WP05)."""
from django.urls import path

from datara.views import (
    DataraLoginView,
    DataraLogoutView,
    home,
    recorded_metric_api,
    recorded_metric_evidence_api,
    recorded_metric_page,
)


urlpatterns = [
    path("", home, name="home"),
    path("login/", DataraLoginView.as_view(), name="login"),
    path("logout/", DataraLogoutView.as_view(), name="logout"),
    # Text converters deliberately defer UUID validation until after session,
    # policy, method, rate, and query/body gates in the read dispatcher.
    path("history/recorded-metrics/<str:metric_id>", recorded_metric_page,
         name="recorded_metric_page"),
    path("api/v1/recorded-metrics/<str:metric_id>", recorded_metric_api,
         name="recorded_metric_api"),
    path("api/v1/recorded-metrics/<str:metric_id>/evidence/<str:evidence_id>",
         recorded_metric_evidence_api, name="recorded_metric_evidence_api"),
]
