from django.urls import path
from apis_acdhch_django_auditlog.views import AuditLog, UserAuditLog

app_name = "acdh_django_auditlog"

urlpatterns = [
    path("profile/auditlog", UserAuditLog.as_view(), name="profileauditlog"),
    path("auditlog", AuditLog.as_view(), name="auditlog"),
]
