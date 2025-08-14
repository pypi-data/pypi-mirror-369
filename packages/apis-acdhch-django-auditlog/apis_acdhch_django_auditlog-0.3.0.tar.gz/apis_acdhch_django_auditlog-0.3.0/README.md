# apis_acdhch_django_auditlog

Auditlog integration for APIS apps at the ACDH-CH at the OEAW

# Installation

Add `apis_acdhch_django_auditlog` to your `INSTALLED_APPS`.
Include the apis-acdhch-django-auditlog urls in your `urls.py`:
```
urlpatterns += [path("", include("apis_acdhch_django_auditlog.urls")),]
```
