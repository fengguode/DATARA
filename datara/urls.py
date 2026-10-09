"""Loopback application routes for the approved saved-metric read increment."""
from django.urls import path

from datara.session_identity import LocalLoginView, LocalLogoutView, home
from datara import app_surface, views


urlpatterns = [
    path("", home, name="home"),
    path("login/", LocalLoginView.as_view(), name="login"),
    path("logout/", LocalLogoutView.as_view(), name="logout"),
    path("history/recorded-metrics/<str:metric_id>", views.recorded_metric_page,
         name="recorded-metric-page"),
    path("api/v1/recorded-metrics/<str:metric_id>", app_surface.recorded_metric_detail,
         name="recorded-metric-detail"),
    path("api/v1/recorded-metrics/<str:metric_id>/evidence/<str:evidence_id>",
         app_surface.recorded_metric_evidence, name="recorded-metric-evidence"),
]
