from django.urls import path

from .views import (
    ApplicationListCreateView,
    ApplicationStatusView,
    HealthView,
)


urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("applications/", ApplicationListCreateView.as_view(), name="applications"),
    path(
        "applications/<int:application_id>/status/",
        ApplicationStatusView.as_view(),
        name="application-status",
    ),
]
