from django.contrib import admin
from django.urls import include, path

from .views import index, saml_metadata_view

admin.autodiscover()

urlpatterns = [
    # path("", debug.default_urlconf),
    path("", index),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("social/", include("social_django.urls", namespace="social")),
    path("saml/", saml_metadata_view, name="saml_metadata"),
]
