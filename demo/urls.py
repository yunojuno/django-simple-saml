# import social_auth.urls
from django.contrib import admin
from django.urls import include, path
from django.views import debug

from .views import saml_metadata_view

admin.autodiscover()

urlpatterns = [
    path("", debug.default_urlconf),
    path("admin/", admin.site.urls),
    path("social", include("social_django.urls", namespace="social")),
    path("saml/", saml_metadata_view, name="saml_metadata"),
]
