"""
URL configuration for config project.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # API endpoints (one include per bounded context)
    path("api/", include("core.api.urls")),
    path("api/", include("clientes.api.urls")),
    path("api/", include("oportunidades.api.urls")),
    path("api/", include("pipeline.api.urls")),
    path("api/", include("audit.api.urls")),
    path("api/", include("dashboard.api.urls")),
    # Vanilla Django views (HTML)
    path("", include("clientes.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
