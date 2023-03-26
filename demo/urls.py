from django.contrib import admin
from django.urls import include, path

from .views import index

admin.autodiscover()

urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("social/", include("social_django.urls", namespace="social")),
    path("saml/", include("simple_saml.urls", namespace="simple_saml")),
]
