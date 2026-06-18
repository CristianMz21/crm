"""API URL configuration for the pipeline app."""

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register("endpoint-name", ViewSet, basename="endpoint-name")

urlpatterns = router.urls
