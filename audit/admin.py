from django.contrib import admin
from django.http import HttpRequest

from audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "model", "object_id", "object_repr", "actor", "timestamp")
    list_filter = ("action", "model")
    search_fields = ("object_repr",)
    raw_id_fields = ("actor",)
    readonly_fields = (
        "actor",
        "action",
        "model",
        "object_id",
        "object_repr",
        "changes",
        "timestamp",
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: AuditLog | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: AuditLog | None = None) -> bool:
        return False
